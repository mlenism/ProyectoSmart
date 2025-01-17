from rest_framework import viewsets
from rest_framework.views import APIView
from.serializer import Meterserializer, Alarmaserializer
from .models import Meter, Alarma, Tapa, Falla, Incidencia, Gateway, Hechos, VistaCombinada, EquipStatus, EquipmentStatusLog
from datetime import datetime
import json
import requests
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, filters
from rest_framework.response import Response
from .serializer import UniqueCreatorSerializer, CombinedSerializer, UniqueStatuSerializer, VariableSerializer, EquipmentStatusLogSerializer, DagrunSerializer, Tapaserializer, Fallaserializer, UniqueFallaTypeSerializer, IncidenciaSerializer, GatewaySerializer, CombinedSerializer, VistaCombinadaSerializer, DateRangeSerializer, EquipStatusSerializer, CombinedEquipStatusSerializer
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import CustomPageNumberPagination
from django.db.models import F
from rest_framework import status
from django.conf import settings
from itertools import chain
import os
import mimetypes
from django.db import connection
import base64
from rest_framework.exceptions import ValidationError
##import joblib  # o usar keras si es un modelo Keras
import json

import json
from django.http import JsonResponse
from rest_framework.views import APIView
import os
from django.http import JsonResponse
from rest_framework.views import APIView

import requests
from datetime import datetime
from django.http import JsonResponse
from django.views import View

from django.http import FileResponse, HttpResponse


print(os.path)

class DownloadTemplateView(View):
    def get(self, request, *args, **kwargs):
        # Ruta absoluta o relativa del archivo
        file_path = os.path.join('static', 'templates',  'PLANTILLA - INCIDENCIAS.xlsx')
        
        try:
            # Abrir el archivo en modo binario
            response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="PLANTILLA - INCIDENCIAS.xlsx"'
            return response
        except FileNotFoundError:
            # Retornar un mensaje de error si no se encuentra el archivo
            return HttpResponse("Archivo no encontrado", status=404)


#Vista para el autocomplete de los medidores 
class GatewayAutocompleteView(APIView):

    queryset = Gateway.objects.all()
    serializer_class = GatewaySerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            results = Gateway.objects.filter(gateway_id__icontains=query)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(results, request)
            if page is not None:
                serializer = GatewaySerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = GatewaySerializer(results, many=True)
            return Response(serializer.data)
        return JsonResponse([], safe=False)

# Vista con paginación
class EquipmentStatusLogListView(APIView):
    serializer_class = EquipmentStatusLogSerializer
    pagination_class = CustomPageNumberPagination

    def get(self, request, equip_id):
        # Filtrar los registros según el equip_id
        queryset = EquipmentStatusLog.objects.using('mysql_db').filter(equip_id=equip_id)

        # Configurar la paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        # Serializar los datos de la página
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Si no se aplica paginación, devolver todos los resultados serializados
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class GatewayMySqlCreateView(viewsets.ModelViewSet):
    serializer_class = CombinedEquipStatusSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        return EquipStatus.objects.none()  # Retorna un queryset vacío.

    def list(self, request, *args, **kwargs):
        gateway_id = request.query_params.get('gateway_id', None)

        # Obtener lista de gateway_ids
        if gateway_id:
            gateway_id_list = [c.strip() for c in gateway_id.split(',')]
        else:
            gateway_id_list = list(Gateway.objects.values_list('gateway_id', flat=True))

        # Consultar EquipStatus en MySQL
        queryset = EquipStatus.objects.using('mysql_db').filter(equip_id__in=gateway_id_list)

        # Identificar gateways faltantes
        missing_gateways = set(gateway_id_list) - set(queryset.values_list('equip_id', flat=True))

        # Consultar en el segundo servidor MySQL solo si faltan gateways
        queryset_other_server = []
        if missing_gateways:
            queryset_other_server = EquipStatus.objects.using('mysql_db_ygp2').filter(equip_id__in=missing_gateways)

        # Convertir los querysets en listas y combinarlos
        combined_results = list(queryset) + list(queryset_other_server)

        # Obtener datos de Gateway desde PostgreSQL
        gateway_data = Gateway.objects.filter(gateway_id__in=gateway_id_list).values(
            'gateway_id', 'latitude', 'longitude', 'service_center'
        )
        gateway_data_dict = {gw['gateway_id']: gw for gw in gateway_data}

        # Preparar datos de respuesta combinando los datos de EquipStatus y Gateway
        response_data = []
        for gateway in combined_results:
            equip_id = gateway.equip_id
            gateway_info = gateway_data_dict.get(equip_id, {'latitude': None, 'longitude': None, 'service_center': None})

            response_data.append({
                'equip_id': gateway.equip_id,
                'latitude': gateway_info['latitude'],
                'longitude': gateway_info['longitude'],
                'service_center': gateway_info['service_center'],
                'last_update_time': gateway.last_update_time,
                'online_status': gateway.online_status,
                # Otros campos según sea necesario
            })

        # Ordenar resultados si se proporciona un parámetro de ordenación
        ordering = request.query_params.get('ordering')
        if ordering:
            reverse = ordering.startswith('-')
            ordering_key = ordering.lstrip('-')
            response_data.sort(key=lambda x: x.get(ordering_key), reverse=reverse)

        # Paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(response_data, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Si no hay paginación, devolver el conjunto completo
        serializer = self.get_serializer(response_data, many=True)
        return Response(serializer.data)


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

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')  # Obtener el archivo de la solicitud
        if not file:
            return Response({"error": "No se proporcionó ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el archivo sea un Excel
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
            return Response({"error": "El archivo proporcionado no es un archivo Excel."}, status=status.HTTP_400_BAD_REQUEST)

        # Renombrar el archivo a "incidencias"
        new_filename = 'incidencias.xlsx'
        save_path = os.path.join(settings.MEDIA_ROOT, new_filename)

        # Guardar el archivo en la ruta especificada
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return Response({"message": f"Archivo {new_filename} subido exitosamente."}, status=status.HTTP_201_CREATED)

class AlarmasIncidenciasView(APIView):
    pagination_class = CustomPageNumberPagination  # Usa la clase de paginación personalizada

    def get(self, request, *args, **kwargs):
        # Obtener parámetros de consulta
        queryset = list(chain(
            ({'tipo': 'alarma', 'data': item} for item in Alarma.objects.all()),
            ({'tipo': 'incidencia', 'data': item} for item in Incidencia.objects.all())
        ))
        # Paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        data = CombinedSerializer(page, many=True)

        return paginator.get_paginated_response(data.data)


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

class VistaCombinadaCreateView(viewsets.ModelViewSet):
    
    queryset = VistaCombinada.objects.all()

    serializer_class = VistaCombinadaSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'meter_code', 'fecha', 'tipo', 'falla_desc']

    
    def get_queryset(self):
        
        # Agregar falla_desc al queryset para facilitar el ordenamiento
        queryset = super().get_queryset().annotate(falla_desc=F('falla__falla_desc'))

        id = self.request.query_params.get('id') #Habilitar filtrado por status
        fecha = self.request.query_params.get('fecha') #Habilitar filtrado por tapa_id
        falla = self.request.query_params.get('falla') #Habilitar filtrado por create_date
        meter_code = self.request.query_params.get('meter_code') #Habilitar filtrado por create_date
        falla_desc = self.request.query_params.get('falla_desc') #Habilitar filtrado por tapa_id
        falla_type = self.request.query_params.get('falla_type') #Habilitar filtrado por tapa_id
        fecha_gte = self.request.query_params.get('fecha_gte')
        fecha_lte = self.request.query_params.get('fecha_lte')

        if id:
            # Split the creator query parameter by comma to handle multiple values
            id_list = [c.strip() for c in id.split(',')]
            queryset = queryset.filter(id__in=id_list)
        if fecha:
            # Convertir las fechas del formato YYYY/MM/DD a YYYY-MM-DD
            fecha_list = [self.convert_fecha_format(c.strip()) for c in fecha.split(',')]
            queryset = queryset.filter(fecha__in=fecha_list)
        if falla:
            queryset = queryset.filter(falla=falla)
        if meter_code:
            queryset = queryset.filter(meter_code=meter_code)
        if falla_desc:
            falla_desc_list = [c.strip() for c in falla_desc.split(',')]
            queryset = queryset.filter(falla__falla_desc__in=falla_desc_list)
        if falla_type:
            falla_type_list = [c.strip() for c in falla_type.split(',')]
            queryset = queryset.filter(falla__falla_type__in=falla_type_list)
        # Procesar y filtrar fecha_gte y fecha_lte
        if fecha_gte:
            fecha_gte = self.validate_and_convert_date(fecha_gte)
            if fecha_gte:
                queryset = queryset.filter(fecha__gte=fecha_gte)
        if fecha_lte:
            fecha_lte = self.validate_and_convert_date(fecha_lte)
            if fecha_lte:
                queryset = queryset.filter(fecha__lte=fecha_lte)

        return queryset

    def validate_and_convert_date(self, date_str):
        """
        Valida y convierte un string de fecha en formato aceptable.
        Soporta los formatos YYYYMMDD y YYYY-MM-DD.
        """
        formats = ['%Y%m%d', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None  # Retorna None si ningún formato es válido
    
    def convert_fecha_format(self, fecha_str):
        """
        Convierte una fecha del formato YYYY/MM/DD hh:mm:ss al formato YYYY-MM-DD hh:mm:ss
        """
        try:
            # Parsear la fecha de la cadena con el formato 'YYYY/MM/DD hh:mm:ss'
            fecha_obj = datetime.strptime(fecha_str, '%Y/%m/%d %H:%M:%S')
            # Retornar la fecha en el formato 'YYYY-MM-DD hh:mm:ss'
            return fecha_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None  # Manejar el caso donde el formato de fecha no es válido
        
class CombinedAutocompleteView(APIView):
    queryset = VistaCombinada.objects.all()
    serializer_class = VistaCombinadaSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'meter_code', 'fecha', 'tipo', 'falla_desc']


    def get(self, request):
        query = request.GET.get('q', '')
        fecha_gte = request.GET.get('fecha_gte')
        fecha_lte = request.GET.get('fecha_gte_lte')
        fecha_exact = request.GET.get('fecha_exact')

        results = VistaCombinada.objects.all()

        if query:
            results = results.filter(meter_code__icontains=query)

        # Aplicar filtros de rango y exactitud
        if fecha_gte:
            results = results.filter(fecha__gte=fecha_gte)
        if fecha_lte:
            results = results.filter(fecha__lte=fecha_lte)
        if fecha_exact:
            results = results.filter(fecha_id=fecha_exact)

        # Ordenar los resultados
        results = results.order_by(
            F('fecha').desc(nulls_last=True),
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        if page is not None:
            serializer = VistaCombinadaSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = VistaCombinadaSerializer(results, many=True)
        return Response(serializer.data)

class GatewayCreateView(viewsets.ModelViewSet):
    
    queryset = Gateway.objects.all()

    serializer_class = GatewaySerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['gateway_id',
                       'status'
                       'latitude',
                       'longitude',
                       'service_center'
                        ]
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        gateway_id = self.request.query_params.get('gateway_id') #Habilitar filtrado por status
        status = self.request.query_params.get('status') #Habilitar filtrado por tapa_id
        latitude = self.request.query_params.get('latitude') #Habilitar filtrado por create_date
        longitude = self.request.query_params.get('longitude') #Habilitar filtrado por create_date
        service_center = self.request.query_params.get('service_center') #Habilitar service_center

        if gateway_id:
            # Split the creator query parameter by comma to handle multiple values
            gateway_id_list = [c.strip() for c in gateway_id.split(',')]
            queryset = queryset.filter(gateway_id__in=gateway_id_list)
        if status:
            queryset = queryset.filter(status=status)
        if latitude:
            queryset = queryset.filter(latitude=latitude)
        if longitude:
            queryset = queryset.filter(longitude=longitude)
        if service_center:
            # Split the creator query parameter by comma to handle multiple values
            service_center_list = [c.strip() for c in service_center.split(',')]
            queryset = queryset.filter(service_center__in=service_center_list)
        return queryset



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
    

# Vista para alarmas
class AlarmViewSet(viewsets.ModelViewSet):

    queryset = Alarma.objects.all()  # Define el queryset aquí

    # Serializador de los medidores
    serializer_class = Alarmaserializer
    pagination_class = CustomPageNumberPagination

    # Filtros del backend
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    ordering_fields = ['alarm_time_id', 
                       'alarm_timestamp_id', 
                       'meter_code',
                       'falla__falla_desc',
                       'alarm_pk',
                       'falla_type']  # Añade estos campos a los campos ordenables

    def get_queryset(self):
        queryset = super().get_queryset()
        falla_desc = self.request.query_params.get('falla_desc')
        falla_type = self.request.query_params.get('falla_type')
        alarm_pk = self.request.query_params.get('alarm_pk')
        alarm_time_id_gte = self.request.query_params.get('alarm_time_id_gte')
        alarm_time_id_lte = self.request.query_params.get('alarm_time_id_lte')
        alarm_time_id_exact = self.request.query_params.get('alarm_time_id_exact')
        meter_code = self.request.query_params.get('meter_code')


        ordering = self.request.query_params.get('ordering', None)

        if falla_type:
            falla_type_list = [c.strip() for c in falla_type.split(',')]
            queryset = queryset.filter(falla__falla_type__in=falla_type_list)
        if falla_desc:
            falla_desc_list = [c.strip() for c in falla_desc.split(',')]
            queryset = queryset.filter(falla__falla_desc__in=falla_desc_list)
        if alarm_pk:
            queryset = queryset.filter(alarm_pk=alarm_pk)
        if alarm_time_id_gte:
            queryset = queryset.filter(alarm_time_id__gte=alarm_time_id_gte)
        if alarm_time_id_lte:
            queryset = queryset.filter(alarm_time_id__lte=alarm_time_id_lte)
        if alarm_time_id_exact:
            queryset = queryset.filter(alarm_time_id=alarm_time_id_exact)

        
        # Filtro por meter_code
        if meter_code:
            meter_code_list = [code.strip() for code in meter_code.split(',')]
            queryset = queryset.filter(meter_code__in=meter_code_list)
    
        if ordering:
            if ordering == 'alarm_date':
                # Ordenar por create_time_id y create_ts_id en orden descendente
                queryset = queryset.order_by(
                    F('alarm_time_id').desc(nulls_last=True),
                    F('alarm_timestamp_id').desc(nulls_last=True)
                )
            elif ordering.startswith('-alarm_date'):
                # Ordenar por create_time_id y create_ts_id en orden ascendente
                queryset = queryset.order_by(
                    F('alarm_time_id').asc(nulls_last=True),
                    F('alarm_timestamp_id').asc(nulls_last=True)
                )

        return queryset
    


@method_decorator(csrf_exempt, name='dispatch')
class TriggerDagRunView(View):
    def post(self, request, dag_id):
        try:
            body = json.loads(request.body)
            url = f"http://localhost:8080/api/v1/dags/{dag_id}/dagRuns"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.post(url, headers=headers, json=body, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
#Vista para el manejo de solicitudes get de las variables seteadas en el apache airflow
@method_decorator(csrf_exempt, name='dispatch')
class GetVariables(View):

    serializer_class = VariableSerializer

    def get(request, *args, **kwargs):
        try:
            url = f"http://localhost:8080/api/v1/variables"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.get(url, headers=headers, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

#Vista para el manejo de solicitudes get de los dag_runs seteadas en el apache airflow
@method_decorator(csrf_exempt, name='dispatch')
class GetDagRuns(View):

    serializer_class = DagrunSerializer

    def get(request, *args, **kwargs):
        try:
            #Cambiar STG4_MEDIDORES por el nombre del dag principal del workflow
            url = f"http://localhost:8080/api/v1/dags/STG4_MEDIDORES/dagRuns?limit=1&order_by=-start_date"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.get(url, headers=headers, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

#Vista para los creadores únicos
class UniqueCreatorListView(generics.GenericAPIView):
    serializer_class = UniqueCreatorSerializer

    def get(self, request, *args, **kwargs):
        unique_creators = Meter.objects.values_list('creator', flat=True).distinct()
        response_data = {'unique_creators': list(unique_creators)}
        return Response(response_data)
    
#Vista para las etiquetas únicas
class UniqueStatusListView(generics.GenericAPIView):
    serializer_class = UniqueStatuSerializer

    def get(self, request, *args, **kwargs):
        unique_creators = Meter.objects.values_list('status', flat=True).distinct()
        response_data = {'unique_status': list(unique_creators)}
        return Response(response_data)
    
#Vista para las tapas únicas
class UniqueTapasListView(viewsets.ModelViewSet):
    queryset = Tapa.objects.all()  # Define el queryset aquí

    # Serializador de los medidores
    serializer_class = Tapaserializer
    pagination_class = CustomPageNumberPagination

    # Filtros del backend
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        tapa_id = self.request.query_params.get('tapa_id')
        tapa_desc = self.request.query_params.get('tapa_desc')

        if tapa_id:
            queryset = queryset.filter(tapa_id=tapa_id)
        if tapa_desc:
            queryset = queryset.filter(tapa_desc=tapa_desc)
        return queryset
    
#Vista para las tapas únicas
class UniqueFallasDescListView(viewsets.ModelViewSet):
    queryset = Falla.objects.all()  # Define el queryset aquí

    # Serializador de los medidores
    serializer_class = Fallaserializer
    pagination_class = CustomPageNumberPagination

    # Filtros del backend
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        falla_id = self.request.query_params.get('falla_id')
        falla_desc = self.request.query_params.get('falla_desc')
        falla_type = self.request.query_params.get('falla_type')

        if falla_id:
            queryset = queryset.filter(falla_id=falla_id)
        if falla_desc:
            queryset = queryset.filter(falla_desc=falla_desc)
        if falla_type:
            falla_type_list = [c.strip() for c in falla_type.split(',')]
            queryset = queryset.filter(falla_type__in=falla_type_list)
        return queryset
    
#Vista para los creadores únicos
class UniqueFallaTypeListView(generics.GenericAPIView):
    serializer_class = UniqueFallaTypeSerializer

    def get(self, request, *args, **kwargs):
        unique_creators = Falla.objects.values_list('falla_type', flat=True).distinct()
        response_data = {'unique_falla_type': list(unique_creators)}
        return Response(response_data)

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
    
class AlarmaAutocompleteView(APIView):
    queryset = Alarma.objects.all()
    serializer_class = Alarmaserializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['alarm_time_id', 
                       'alarm_timestamp_id', 
                       'meter_code',
                       'falla__falla_desc',
                       'alarm_pk',
                       'falla_type']

    def get(self, request):
        query = request.GET.get('q', '')
        alarm_time_id_gte = request.GET.get('alarm_time_id_gte')
        alarm_time_id_lte = request.GET.get('alarm_time_id_lte')
        alarm_time_id_exact = request.GET.get('alarm_time_id_exact')

        results = Alarma.objects.all()

        if query:
            results = results.filter(meter_code__icontains=query)

        # Aplicar filtros de rango y exactitud
        if alarm_time_id_gte:
            results = results.filter(alarm_time_id__gte=alarm_time_id_gte)
        if alarm_time_id_lte:
            results = results.filter(alarm_time_id__lte=alarm_time_id_lte)
        if alarm_time_id_exact:
            results = results.filter(alarm_time_id=alarm_time_id_exact)

        # Ordenar los resultados
        results = results.order_by(
            F('alarm_time_id').desc(nulls_last=True),
            F('alarm_timestamp_id').desc(nulls_last=True)
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        if page is not None:
            serializer = Alarmaserializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = Alarmaserializer(results, many=True)
        return Response(serializer.data)

#class SumaUltimoValor(generics.GenericAPIView):
#    serializer_class = SumaUltimoValorSerializer

#    def get(self, request, *args, **kwargs):
        # Obtener la fecha actual en la zona horaria de Perú
#        peru_tz = pytz.timezone('America/Lima')
#        now = datetime.now(peru_tz)

        # Calcular el primer día del mes actual
#        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Convertir la fecha a formato yyyy-mm-dd para el filtro
#        first_day_str = first_day_of_month.strftime('%Y%m%d')

        # Obtener los creadores únicos y sus medidores en una sola consulta
#        creators_with_meters = Meter.objects.values('creator', 'meter_code')

#        print(creators_with_meters)
        # Consulta para obtener el valor más reciente para cada medidor y su suma
        # Filtrar los hechos para el mes actual
#        queryset = Hechos.objects.filter(
#            meter_id__in=[meter_code for _, meter_code in creators_with_meters],
#            recv_time_id__gte=first_day_str
#        ).values('meter_id').annotate(
#            last_value=Max('real_volume')
#        ).values('meter_id', 'last_value')

        # Calcular la suma total por creador
#        result = {}
#        for creator, meter_code in creators_with_meters:
#            total_volume = queryset.filter(
#                meter_id=meter_code
#            ).aggregate(total_volume=Sum('last_value'))['total_volume']
#            result[creator] = total_volume if total_volume else 0

        # Retornar el resultado en una respuesta JSON
#        return Response(result)
