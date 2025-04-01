from rest_framework import serializers
from .models import Description
from django.contrib.auth.models import User

class DescriptionSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    owner_email = serializers.ReadOnlyField(source='owner.email')
    owner_isSuperuser = serializers.ReadOnlyField(source='owner.is_superuser')
    owner_dateJoined = serializers.SerializerMethodField()

    class Meta:
        model = Description
        fields = '__all__'
        extra_kwargs = {'owner': {'required': False}}

    def get_owner_dateJoined(self, obj):
        return obj.owner.date_joined.strftime('%Y-%m-%d')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    descriptions = DescriptionSerializer(many=True, required=False)  # Se pueden agregar descripciones opcionales

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'descriptions']

    def create(self, validated_data):
        descriptions_data = validated_data.pop('descriptions', [])  # Extrae descripciones si se incluyen
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        # Crear descripciones asociadas al usuario
        for desc_data in descriptions_data:
            Description.objects.create(owner=user, **desc_data)

        return user
