from rest_framework import serializers
from .models import Incidencia
from apiSmart.meters.models import Meterdata

#Serializador para los registros de incidencias
class IncidenciaSerializer(serializers.ModelSerializer):

    meter_id = serializers.SlugRelatedField(source='meter_code', slug_field='meter_id', read_only=True)

    falla_desc = serializers.SerializerMethodField()

    falla_type = serializers.SerializerMethodField()
    
    usuario = serializers.SlugRelatedField(source='meter_code', slug_field='creator', read_only=True)

    tapa_desc = serializers.SerializerMethodField()

    direccion = serializers.SerializerMethodField()

    cliente = serializers.SerializerMethodField()

    class Meta:
        model = Incidencia
        fields = ['incidencia_id',
                  'meter_code',
                  'cliente',
                  'direccion',
                  'meter_id',
                  'falla_desc',
                  'fecha_incidencia',
                  'usuario',
                  'tapa_desc',
                  'img',
                  'encargado',
                  'falla_type',
                  'falla',
                  ]

    def get_falla_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_desc if obj.falla else None

    def get_falla_type(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_type if obj.falla else None

    def get_tapa_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.meter_code.tapa.tapa_desc if obj.meter_code.tapa else None

    def get_direccion(self, obj):
        try:
            data = Meterdata.objects.get(meter_code=obj.meter_code)
            address = data.address
            return address
        except Meterdata.DoesNotExist:
            return None

    def get_cliente(self, obj):
        try:
            data = Meterdata.objects.get(meter_code=obj.meter_code)
            customer = data.costumer
            return customer
        except Meterdata.DoesNotExist:
            return None