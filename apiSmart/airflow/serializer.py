from rest_framework import serializers

#Serializador para las variables únicos
class VariableSerializer(serializers.Serializer):
    variable = serializers.CharField()

#Serializador para los estados de medidor o etiquetas únicos
class DagrunSerializer(serializers.Serializer):
    dagrun = serializers.CharField()