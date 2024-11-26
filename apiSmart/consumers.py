import json
import requests
from requests.auth import HTTPBasicAuth
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class DataPollingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.polling_task = asyncio.create_task(self.poll_data())

    async def disconnect(self, close_code):
        if hasattr(self, 'polling_task'):
            self.polling_task.cancel()

    async def poll_data(self):
        url_dag_run = 'http://localhost:8080/api/v1/dags/WF_INCIDENCIAS/dagRuns?limit=1&order_by=-start_date'
        auth = HTTPBasicAuth('airflow', 'airflow')
        polling_logs = False  # Bandera para alternar entre llamar a dag_run o logs
        retry_count = 0
        max_retries = 15  # Límite de intentos

        while True:
            try:
                if not polling_logs:
                    # Solicita el último `dag_run_id` y su estado
                    response = requests.get(url_dag_run, auth=auth)
                    response.raise_for_status()
                    dag_runs_data = response.json()
                    dag_run = dag_runs_data["dag_runs"][0]  # Extraer el primer `dag_run`
                    dag_run_id = dag_run["dag_run_id"]
                    dag_run_state = dag_run["state"]  # Extraer el estado del `dag_run`

                    print(f"Obtained dag_run_id: {dag_run_id}, State: {dag_run_state}")

                    # Si no es 'success', empieza a hacer polling de logs
                    url = f'http://localhost:8080/api/v1/dags/WF_INCIDENCIAS/dagRuns/{dag_run_id}/taskInstances/run_hop_pipeline/logs/1?full_content=true'
                    polling_logs = True  # Cambia la bandera para hacer polling de logs
                    retry_count = 0  # Reinicia el contador de reintentos

                else:
                    # Realiza la solicitud de logs
                    response = requests.get(url, auth=auth)

                    if response.status_code == 404:
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"Error 404 recibido. Intentando de nuevo ({retry_count}/{max_retries})...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            await self.send(text_data=json.dumps({
                                'error': 'Error 404 repetido. Máximo de intentos alcanzado.'
                            }))
                            polling_logs = False  # Reinicia para volver a chequear el estado del `dag_run`
                            continue

                    response.raise_for_status()
                    data = response.text
                    print("Received data:", data)
                    
                    # Después de enviar los logs, verificar nuevamente el estado del `dag_run`
                    response = requests.get(url_dag_run, auth=auth)
                    response.raise_for_status()
                    dag_runs_data = response.json()
                    dag_run_state = dag_runs_data["dag_runs"][0]["state"]

                    if dag_run_state == "success":
                        await self.send(text_data=json.dumps({
                            'message': 'Workflow ejecutado con éxito',
                            'content': data,
                            'state': 'success'
                        }))
                        polling_logs = False  # Deja de hacer polling de logs si el estado cambia a "success"
                    
                    if dag_run_state == "failed":
                        await self.send(text_data=json.dumps({
                            'message': 'Workflow se detuvo, error inesperado',
                            'content': data,
                            'state' : 'failed'
                        }))
                        polling_logs = False  # Deja de hacer polling de logs si el estado cambia a "success"

                    if dag_run_state == "running":
                        await self.send(text_data=json.dumps({
                            'message': 'Workflow en ejecución',
                            'content': data,
                            'state': 'running'
                        }))
                        polling_logs = False  # Deja de hacer polling de logs si el estado cambia a "success"

                await asyncio.sleep(2)  # Espera antes de la siguiente solicitud

            except requests.RequestException as e:
                await self.send(text_data=json.dumps({
                    'error': str(e)
                }))
                await asyncio.sleep(60)  # Espera antes de reintentar
