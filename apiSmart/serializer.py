from rest_framework import serializers
from .models import VistaCombinada
    
#Serializador para los registros de incidencias
class VistaCombinadaSerializer(serializers.ModelSerializer):

    #Descripcion del tipo de tapa
    falla_desc = serializers.SerializerMethodField()
    fecha = serializers.SerializerMethodField()  # Sobrescribir el campo 'fecha'
    falla_type = serializers.SerializerMethodField()  # Sobrescribir el campo 'fecha'

    class Meta:
        model = VistaCombinada
        fields = ['id',
                  'meter_code',
                  'falla_desc',
                  'fecha',
                  'falla',
                  'tipo',
                  'falla_type']  # Incluye todos los campos del modelo Incidencia

    def get_falla_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_desc if obj.falla else None
    
    def get_fecha(self, obj):
        # Formatear la fecha en el formato 'yyyy/mm/dd hh:mm:ss'
        if obj.fecha:
            return obj.fecha.strftime('%Y/%m/%d %H:%M:%S')
        return None
    
    def get_falla_type(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_type if obj.falla else None

class SumaUltimoValorSerializer(serializers.Serializer):
    total_real_volume = serializers.DecimalField(max_digits=20, decimal_places=3, coerce_to_string=False)

