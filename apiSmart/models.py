from django.db import models
from .shared.models import Falla


# Creación del Modelo Alarmas donde se verán los registros de las fallas
class Hechos(models.Model):

    lectura_id = models.CharField(primary_key=True, max_length=255)
    gateway_id = models.CharField(max_length=20)
    eui = models.CharField(max_length=20)
    meter_id = models.CharField(max_length=20)
    real_volume = models.DecimalField(max_digits=20, decimal_places=3)
    recv_time_id = models.IntegerField()
    recv_ts_id = models.IntegerField()
    meter_time = models.IntegerField()

    class Meta:
        db_table = 'smart_med\".\"final_hechos'
        managed = False #No manejar migraciones para esta tabla

# Creación del Modelo Alarmas donde se verán los registros de las fallas
class VistaCombinada(models.Model):

    id = models.CharField(primary_key=True, max_length=255)
    meter_code = models.CharField(max_length=60)
    fecha = models.DateTimeField()
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, db_column='fallo_id', null=True) #fallo_id de incidencias referencia a falla_id de Fallas
    tipo = models.CharField(max_length=255)

    class Meta:
        db_table = 'smart_med\".\"mi_vista_combinada'
        managed = False #No manejar migraciones para esta tabla


