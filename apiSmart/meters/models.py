from django.db import models
from ..shared.models import Tapa

# Create your models here.
class Meter(models.Model):

    meter_id= models.PositiveBigIntegerField(primary_key=True)
    meter_code= models.CharField(max_length=25)
    meter_type= models.CharField(max_length=5)
    model_id = models.PositiveBigIntegerField()
    latitude = models.DecimalField(max_digits=20, decimal_places=17)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)  # Tipo de dato para valores de punto flotante
    tapa = models.ForeignKey(Tapa, on_delete=models.SET_NULL, db_column='tapa_id', null=True) #tapa_id de medidores referenciada en tapa_id de Tapa
    status = models.CharField(max_length=50)
    creator= models.CharField(max_length=64)
    create_time_id = models.IntegerField()  # Campo para la fecha en formato YYYYMMDD
    create_ts_id = models.IntegerField()    # Campo para la hora en formato HHMMSS
    status_update_date = models.DateTimeField()

    class Meta:
        db_table = 'smart_med\".\"final_medidores'
        managed = False #No manejar migraciones para esta tabla, al activarlas cancela las foreign keys