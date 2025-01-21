from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Gateway, EquipStatus, EquipmentStatusLog
from ..pagination import CustomPageNumberPagination
from django.http import JsonResponse
from rest_framework import filters
from rest_framework.response import Response
from .serializer import EquipmentStatusLogSerializer, GatewaySerializer, CombinedEquipStatusSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import JsonResponse


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