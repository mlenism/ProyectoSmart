from rest_framework import serializers
from .models import FinalHechos

class FinalHechosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalHechos
        fields = "__all__" 
