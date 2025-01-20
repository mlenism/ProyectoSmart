from rest_framework import serializers
from .models import Meter, Tapa, Falla, Incidencia, Gateway, VistaCombinada, EquipStatus, EquipmentStatusLog
from datetime import datetime
from .alarms.models import Alarma


class EquipmentStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentStatusLog
        fields = ['log_id', 'equip_id', 'status_time', 'online_status']

class CombinedEquipStatusSerializer(serializers.Serializer):
    equip_id = serializers.CharField(max_length=255)
    online_status = serializers.IntegerField()
    last_update_time = serializers.DateTimeField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    service_center = serializers.CharField(max_length=255, required=False, allow_null=True)

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(format='%Y-%m-%d')
    end_date = serializers.DateField(format='%Y-%m-%d')

class UniqueCreatorSerializer(serializers.Serializer):
    creator = serializers.CharField()

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

#Serializador para los creadores únicos
class Fallaserializer(serializers.ModelSerializer):
    class Meta:
        model=Falla
        fields = [
            'falla_id', #valor viene de la tabla final_tapas
            'falla_desc',
            'falla_type', #valor viene de la tabla final_tapas
            ]

#Serializador para los creadores únicos
class UniqueFallaTypeSerializer(serializers.Serializer):
    fallaType = serializers.CharField()

#Serializador para las variables únicos
class VariableSerializer(serializers.Serializer):
    variable = serializers.CharField()

#Serializador para los estados de medidor o etiquetas únicos
class UniqueStatuSerializer(serializers.Serializer):
    status = serializers.CharField()

#Serializador para los estados de medidor o etiquetas únicos
class DagrunSerializer(serializers.Serializer):
    dagrun = serializers.CharField()

#Serializador para los Medidor
class Meterserializer(serializers.ModelSerializer):

    #Variable para la fecha formateada
    create_date = serializers.SerializerMethodField()

    #Descripcion del tipo de tapa
    tapa_desc = serializers.SerializerMethodField()

    class Meta:
        model=Meter
        fields = [
            'meter_id', 
            'meter_code', 
            'meter_type', 
            'creator', 
            'create_time_id', 
            'create_ts_id',
            'latitude',
            'longitude',
            'status',
            'tapa_id', #valor viene de la tabla final_tapas
            'tapa_desc', #valor viene de la tabla final_tapas
            'create_date', #Valor nuevo creado con los id de fechas
            'status_update_date'
            ]
    
    def get_tapa_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.tapa.tapa_desc if obj.tapa else None

    def get_create_date(self, obj):
        # Convertir los enteros a strings y rellenar ceros a la izquierda si es necesario
        date_str = f"{obj.create_time_id:08d}"
        time_str = f"{obj.create_ts_id:06d}"

        # Convertir a objetos datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            time_obj = datetime.strptime(time_str, "%H%M%S").time()
            # Combinar la fecha y la hora en un solo datetime
            combined_datetime = datetime.combine(date_obj, time_obj)
            # Formatear como "YYYY/MM/DD HH:MM:SS"
            return combined_datetime.strftime("%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None
        
#Serializador para los Medidor
class Alarmaserializer(serializers.ModelSerializer):

    #Variable para la fecha formateada
    alarm_date = serializers.SerializerMethodField()

    #Descripcion del tipo de tapa
    falla_desc = serializers.SerializerMethodField()

    #Descripcion del tipo de tapa
    falla_type = serializers.SerializerMethodField()

    class Meta:
        model=Alarma
        fields = [
            'alarm_pk',
            'alarm_id',
            'meter_code',
            'alarm_time_id',
            'alarm_timestamp_id',
            'recv_time_id',
            'recv_timestamp_id',
            'falla_id', #Valor viene de tabla final_fallas
            'falla_desc', #Valor viene de la tabla final_fallas
            'falla_type', #Valor viene de la tabla final_fallas
            'alarm_date', #Valor nuevo creado con los id de alarm_id
            ]
    
    def get_falla_desc(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_desc if obj.falla else None

    def get_falla_type(self, obj):
        # Obtener el nombre de la tapa a partir del campo tapa_id
        return obj.falla.falla_type if obj.falla else None

    def get_alarm_date(self, obj):
        # Convertir los enteros a strings y rellenar ceros a la izquierda si es necesario
        date_str = f"{obj.alarm_time_id:08d}"
        time_str = f"{obj.alarm_timestamp_id:06d}"

        # Convertir a objetos datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            time_obj = datetime.strptime(time_str, "%H%M%S").time()
            # Combinar la fecha y la hora en un solo datetime
            combined_datetime = datetime.combine(date_obj, time_obj)
            # Formatear como "YYYY/MM/DD HH:MM:SS"
            return combined_datetime.strftime("%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

#Serializador para las Tapas
class Tapaserializer(serializers.ModelSerializer):

    class Meta:
        model=Tapa
        fields = [
            'tapa_id', #valor viene de la tabla final_tapas
            'tapa_desc', #valor viene de la tabla final_tapas
            ]
        
class SumaUltimoValorSerializer(serializers.Serializer):
    total_real_volume = serializers.DecimalField(max_digits=20, decimal_places=3, coerce_to_string=False)
