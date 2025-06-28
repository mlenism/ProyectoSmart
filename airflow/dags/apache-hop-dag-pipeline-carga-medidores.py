from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from airflow.models import Variable


default_args = {
    'owner': 'airflow',
    'description': 'CARGA_MEDIDORES',
    'depend_on_past': False,
    'start_date': datetime(2019, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

schedule_interval = Variable.get("schedule_interval_CARGA_MEDIDORES", default_var="21 * * * *")

with DAG('CARGA_MEDIDORES', 
         default_args=default_args,
         schedule_interval=schedule_interval, 
         catchup=False,
         is_paused_upon_creation=False,
         end_date=datetime(2028, 1, 1)) as dag:
    
    start_dag = DummyOperator(
        task_id='start_dag'
    )
    
    end_dag = DummyOperator(
        task_id='end_dag'
    )
    
    hop = DockerOperator(
        task_id='run_hop_pipeline',
        image='apache/hop:latest',
        api_version='auto',
        auto_remove=True,
        environment={
            'HOP_LOG_LEVEL': 'Basic',
            'HOP_FILE_PATH': '${PROJECT_HOME}/Pipelines/CARGA_MEDIDORES.hpl',
            'HOP_PROJECT_FOLDER': '/files',
            'HOP_PROJECT_NAME': 'ProyectoSmartMed',
            'HOP_RUN_CONFIG': 'local',
            'API_BASE_URL': 'http://host.docker.internal:8000',  # Reemplaza 'localhost' por 'host.docker.internal'
            'HOP_JDBC_JARS': '/files/jars/mysql-connector-j-8.4.0.jar',  # Configuración para el JAR
            'HOP_SHARED_JDBC_FOLDERS': '/opt/hop/lib/jdbc,/jdbc/,/files/jars',  # Carpeta donde se encuentran los JARs
        },
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
        mounts=[
            Mount(source='D:\milto\Desktop\ProyectoSmart\ProyectoSmartMed', target='/files', type='bind'),
        ],
        #command="sh -c 'apt-get update && apt-get install -y mysql-client && run_pipeline_command || tail -f /dev/null'",
        force_pull=False
    )
    
    start_dag >> hop >> end_dag
