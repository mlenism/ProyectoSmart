from rest_framework import serializers
from .models import Gateway, EquipStatus, EquipmentStatusLog

class EquipmentStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentStatusLog
        fields = ['log_id', 'equip_id', 'status_time', 'online_status']

#Serializador para los registros de incidencias
class GatewaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gateway
        fields = ['gateway_id', 
                  'latitude',
                  'longitude',
                  'status',
                  'service_center']

    def get_falla_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_desc if obj.falla else None
    
class EquipStatusSerializer(serializers.ModelSerializer):
    gateway_info = GatewaySerializer(read_only=True)  # Anidar datos del gateway

    class Meta:
        model = EquipStatus
        fields = ['equip_id',
                  'online_status',
                  'last_update_time',
                  'gateway_info']  # Incluye el serializador anidado
        

class CombinedEquipStatusSerializer(serializers.Serializer):
    equip_id = serializers.CharField(max_length=255)
    online_status = serializers.IntegerField()
    last_update_time = serializers.DateTimeField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    service_center = serializers.CharField(max_length=255, required=False, allow_null=True)

