from rest_framework import serializers
from .models import Meter
from datetime import datetime
from .models import Meterdata

#Serializador para los Medidor
class Meterserializer(serializers.ModelSerializer):

    #Variable para la fecha formateada
    create_date = serializers.SerializerMethodField()

    #Descripcion del tipo de tapa
    tapa_desc = serializers.SerializerMethodField()

    #direccion del medidor
    direccion = serializers.SerializerMethodField()

    usuario = serializers.SerializerMethodField()

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
            'status_update_date',
            'cobertura',
            'direccion',
            'usuario'
            ]

    def get_direccion(self, obj):
        try:
            data = Meterdata.objects.get(meter_code=obj.meter_code)
            address = data.address
            return address
        except Meterdata.DoesNotExist:
            return None

    def get_usuario(self, obj):
        try:
            data = Meterdata.objects.get(meter_code=obj.meter_code)
            customer = data.costumer
            return customer
        except Meterdata.DoesNotExist:
            return None
    
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


class MeterdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meterdata
        fields = ['meter_id', 'meter_code', 'costumer', 'address']