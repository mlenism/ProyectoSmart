from rest_framework import serializers
from .models import VistaCombinada
from datetime import datetime

class CombinedSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    id = serializers.IntegerField()
    meter_code = serializers.CharField()
    fallo = serializers.CharField()
    fecha = serializers.DateTimeField()

    def to_representation(self, instance):
        if instance['tipo'] == 'alarma':
            return {
                'tipo': "ALARMA",
                'id': instance['data'].alarm_pk,
                'meter_code': instance['data'].meter_code,
                'fallo': self.get_falla_desc(instance['data']),
                'fecha': self.get_alarm_date(instance['data']),
            }
        elif instance['tipo'] == 'incidencia':
            return {
                'tipo': "INCIDENCIA",
                'id': instance['data'].incidencia_id,
                'meter_code': instance['data'].meter_code,
                'fallo': self.get_falla_desc(instance['data']),
                'fecha': instance['data'].fecha_incidencia,
            }
    
    def get_falla_desc(self, obj):
        # Obtén el campo fallo_desc del modelo Alarma
        return obj.falla.falla_desc if obj.falla else None

    def get_alarm_date(self, obj):
        # Convierte los enteros a strings y rellena ceros a la izquierda si es necesario
        if hasattr(obj, 'alarm_time_id') and hasattr(obj, 'alarm_timestamp_id'):
            date_str = f"{obj.alarm_time_id:08d}"
            time_str = f"{obj.alarm_timestamp_id:06d}"
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                time_obj = datetime.strptime(time_str, "%H%M%S").time()
                # Combina la fecha y la hora en un solo datetime
                combined_datetime = datetime.combine(date_obj, time_obj)
                # Formatea como "YYYY/MM/DD HH:MM:SS"
                return combined_datetime.strftime("%Y/%m/%d %H:%M:%S")
            except ValueError:
                return None
        return None
    
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

