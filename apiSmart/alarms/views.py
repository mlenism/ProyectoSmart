from rest_framework import viewsets
from rest_framework.views import APIView
from .serializer import Alarmaserializer
from .models import Alarma
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..pagination import CustomPageNumberPagination
from django.db.models import F
from rest_framework.views import APIView

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
