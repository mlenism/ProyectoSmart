from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import requests
from django.http import JsonResponse
from django.views import View
from .serializer import DagrunSerializer, VariableSerializer

@method_decorator(csrf_exempt, name='dispatch')
class TriggerDagRunView(View):
    def post(self, request, dag_id):
        try:
            body = json.loads(request.body)
            url = f"http://localhost:8080/api/v1/dags/{dag_id}/dagRuns"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.post(url, headers=headers, json=body, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
#Vista para el manejo de solicitudes get de los dag_runs seteadas en el apache airflow
@method_decorator(csrf_exempt, name='dispatch')
class GetDagRuns(View):

    serializer_class = DagrunSerializer

    def get(request, *args, **kwargs):
        try:
            #Cambiar STG4_MEDIDORES por el nombre del dag principal del workflow
            url = f"http://localhost:8080/api/v1/dags/STG4_MEDIDORES/dagRuns?limit=1&order_by=-start_date"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.get(url, headers=headers, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
#Vista para el manejo de solicitudes get de las variables seteadas en el apache airflow
@method_decorator(csrf_exempt, name='dispatch')
class GetVariables(View):

    serializer_class = VariableSerializer

    def get(request, *args, **kwargs):
        try:
            url = f"http://localhost:8080/api/v1/variables"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            auth = ('airflow', 'airflow')
            response = requests.get(url, headers=headers, auth=auth)
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

