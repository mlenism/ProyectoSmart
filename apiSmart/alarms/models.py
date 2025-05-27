from django.db import models
from apiSmart.shared.models import Falla
from apiSmart.meters.models import Meter

class Alarma(models.Model):
    alarm_pk = models.PositiveBigIntegerField(primary_key=True)
    alarm_id = models.CharField(max_length=25)
    meter_code = models.ForeignKey(Meter, on_delete=models.SET_NULL, db_column='meter_code', null=True)
    alarm_time_id = models.IntegerField()  # Campo para la fecha en formato YYYYMMDD
    alarm_timestamp_id = models.IntegerField()    # Campo para la hora en formato HHMMSS
    recv_time_id = models.IntegerField()  # Campo para la fecha en formato YYYYMMDD
    recv_timestamp_id = models.IntegerField()    # Campo para la hora en formato HHMMSS
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, db_column='fallo_id', null=True) #fallo_id de alarmas referencia a falla_id de Fallas

    class Meta:
        db_table = 'smart_med\".\"final_alarmas'
        managed = False #No manejar migraciones para esta tabla