from rest_framework import serializers
from .models import Incidencia

#Serializador para los registros de incidencias
class IncidenciaSerializer(serializers.ModelSerializer):

    #Descripcion del tipo de tapa
    falla_desc = serializers.SerializerMethodField()

    class Meta:
        model = Incidencia
        fields = ['incidencia_id',
                  'meter_code',
                  'falla_desc',
                  'fecha_incidencia',
                  'falla',
                  'encargado',
                  'img']  # Incluye todos los campos del modelo Incidencia

    def get_falla_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_desc if obj.falla else None