from rest_framework import generics, viewsets, filters
from .serializer import UniqueCreatorSerializer, UniqueFallaTypeSerializer, UniqueStatuSerializer, Tapaserializer, Fallaserializer
from rest_framework.response import Response
from ..pagination import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from ..meters.models import Meter
from ..shared.models import Tapa, Falla

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