import django_filters
from .models import Meter, Alarma

class MeterFilter(django_filters.FilterSet):
    creator = django_filters.CharFilter(lookup_expr='icontains')  # Filtra insensible a mayúsculas/minúsculas
    status = django_filters.CharFilter(lookup_expr='icontains')
    tapa_id = django_filters.CharFilter(lookup_expr='icontains')
    create_date = django_filters.CharFilter(lookup_expr='icontains')
    meter_code = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Meter
        fields = ['creator','status','tapa_id','create_date','meter_code']

class AlarmaFilter(django_filters.FilterSet):
    alarm_pk = django_filters.NumberFilter(lookup_expr='icontains')
    alarm_time_id_gte = django_filters.NumberFilter(field_name='alarm_time_id', lookup_expr='gte')
    alarm_time_id_lte = django_filters.NumberFilter(field_name='alarm_time_id', lookup_expr='lte')
    alarm_time_id_exact = django_filters.NumberFilter(field_name='alarm_time_id', lookup_expr='exact')

    class Meta:
        model = Alarma
        fields = ['alarm_time_id_gte', 'alarm_time_id_lte', 'alarm_time_id_exact', 'alarm_pk']

