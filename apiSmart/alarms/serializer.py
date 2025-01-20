from rest_framework import serializers
from .models import Alarma
from datetime import datetime

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