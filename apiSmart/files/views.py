import os
import mimetypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.views import View

class DownloadTemplateView(View):
    def get(self, request, *args, **kwargs):
        # Ruta absoluta o relativa del archivo
        file_path = os.path.join('static', 'templates',  'PLANTILLA - INCIDENCIAS.xlsx')
        
        try:
            # Abrir el archivo en modo binario
            response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="PLANTILLA - INCIDENCIAS.xlsx"'
            return response
        except FileNotFoundError:
            # Retornar un mensaje de error si no se encuentra el archivo
            return HttpResponse("Archivo no encontrado", status=404)

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')  # Obtener el archivo de la solicitud
        if not file:
            return Response({"error": "No se proporcionó ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el archivo sea un Excel
        mime_type, _ = mimetypes.guess_type(file.name)
        valid_mime_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']

        # Validar MIME y extensión como respaldo
        if mime_type not in valid_mime_types and not file.name.endswith(('.xls', '.xlsx')):
            return Response({"error": "El archivo proporcionado no es un archivo Excel válido."}, status=status.HTTP_400_BAD_REQUEST)

        # Renombrar el archivo a "incidencias"
        new_filename = 'incidencias.xlsx'
        save_path = os.path.join(settings.MEDIA_ROOT, new_filename)
        save_path = os.path.normpath(save_path)  # Normaliza la ruta antes de usarla


        # Guardar el archivo en la ruta especificada
        try:
            with open(save_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except Exception as e:
            return Response({"error": f"Error al guardar el archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Archivo {new_filename} subido exitosamente."}, status=status.HTTP_201_CREATED)
