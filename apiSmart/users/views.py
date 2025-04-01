from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Description
from.serializer import DescriptionSerializer, UserRegistrationSerializer
from ..pagination import CustomPageNumberPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_descriptions(request):
    user = request.user
    if user.is_superuser:
        descriptions = Description.objects.all()  # Devuelve todas las descripciones si es superusuario
    else:
        descriptions = Description.objects.filter(owner=user)  # Solo sus propias descripciones

    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(descriptions, request)

    serializer = DescriptionSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logOut(request):
    try:
        response = Response()
        response.delete_cookie('access_token', path='/', samesite='None')
        response.delete_cookie('refresh_token', path='/', samesite='None')
        response.data = {'success': True}
        return response
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Permite que cualquier usuario acceda
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "Usuario creado exitosamente", "user": serializer.data}, status=201)
    return Response(serializer.errors, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    if request.user.is_authenticated:
        return Response({'authenticated': True})
    return Response({'authenticated': False}, status=401)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    user = request.user
    
    # Verificar si el usuario es superusuario
    if not user.is_superuser:
        return Response({"error": "No tienes permiso para eliminar usuarios."}, status=403)
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Evitar que un superusuario se elimine a sí mismo
        if user == user_to_delete:
            return Response({"error": "No puedes eliminar tu propia cuenta."}, status=400)

        user_to_delete.delete()
        return Response({"message": f"Usuario {user_to_delete.username} eliminado exitosamente."}, status=200)
    
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=404)

