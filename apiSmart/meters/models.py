from django.db import models
from ..shared.models import Tapa

# Create your models here.
class Meter(models.Model):

    meter_code= models.CharField(max_length=25, primary_key=True)
    meter_id = models.PositiveBigIntegerField()
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
    cobertura = models.CharField(max_length=64)

    class Meta:
        db_table = 'smart_med\".\"final_medidores'
        managed = False #No manejar migraciones para esta tabla, al activarlas cancela las foreign keys

    def __str__(self):
        str = ("MEDIDOR\n"
        f"meter_id: {self.meter_id}\n"
        f"meter_code: {self.meter_code}\n"
        f"meter_type: {self.meter_type}\n"
        f"model_id: {self.model_id}\n"
        f"latitude: {self.latitude}\n"
        f"longitude: {self.longitude}\n"
        f"tapa: {self.tapa}\n"
        f"status: {self.status}\n"
        f"creator: {self.creator}\n"
        f"create_time_id: {self.create_time_id}\n"
        f"create_ts_id: {self.create_ts_id}\n"
        f"status_update_date: {self.status_update_date}\n"
        f"cobertura: {self.cobertura}")
        return str


class Meterdata(models.Model):
    meter_id = models.PositiveBigIntegerField(primary_key=True)
    meter_code = models.ForeignKey(Meter, on_delete=models.SET_NULL, db_column='meter_code', null=True)
    costumer = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'smart_med"."final_meterdata'
        managed = False

    def __str__(self):
        str = ("METERDATA\n"
        f"meter_id: {self.meter_id}\n"
        f"meter_code: {self.meter_code}\n"
        f"costumer: {self.costumer}\n"
        f"address: {self.address}")
        return str
