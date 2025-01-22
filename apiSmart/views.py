from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Hechos, VistaCombinada
from datetime import datetime
from rest_framework import filters
from rest_framework.response import Response
from .serializer import VistaCombinadaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import CustomPageNumberPagination
from django.db.models import F
##import joblib  # o usar keras si es un modelo Keras
from datetime import datetime

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
