from rest_framework import serializers
from .models import Alarma
from datetime import datetime
from apiSmart.meters.models import Meterdata

class Alarmaserializer(serializers.ModelSerializer):

    meter_id = serializers.SlugRelatedField(source='meter_code', slug_field='meter_id', read_only=True)

    statuss = serializers.SlugRelatedField(source='meter_code', slug_field='status', read_only=True)

    alarm_date = serializers.SerializerMethodField()

    falla_descc = serializers.SerializerMethodField()

    falla_type = serializers.SerializerMethodField()

    direccion = serializers.SerializerMethodField()

    cliente = serializers.SerializerMethodField()

    class Meta:
        model=Alarma
        fields = [
            'alarm_pk',
            'alarm_id',
            'meter_code',
            'meter_id',
            'cliente',
            'direccion',
            'alarm_time_id',
            'alarm_timestamp_id',
            'recv_time_id',
            'recv_timestamp_id',
            'falla_id', 
            'falla_descc', 
            'alarm_date',
            'falla_type',
            'statuss'
            ]
    
    def get_falla_descc(self, obj):
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