from rest_framework import serializers
from ..shared.models import Falla, Tapa


class UniqueCreatorSerializer(serializers.Serializer):
    creator = serializers.CharField()


#Serializador para los creadores únicos
class UniqueFallaTypeSerializer(serializers.Serializer):
    fallaType = serializers.CharField()

#Serializador para los estados de medidor o etiquetas únicos
class UniqueStatuSerializer(serializers.Serializer):
    status = serializers.CharField()

#Serializador para los creadores únicos
class Fallaserializer(serializers.ModelSerializer):
    class Meta:
        model=Falla
        fields = [
            'falla_id', #valor viene de la tabla final_tapas
            'falla_desc',
            'falla_type', #valor viene de la tabla final_tapas
            ]
        
#Serializador para las Tapas
class Tapaserializer(serializers.ModelSerializer):
    class Meta:
        model=Tapa
        fields = [
            'tapa_id', #valor viene de la tabla final_tapas
            'tapa_desc', #valor viene de la tabla final_tapas
            ]
        

