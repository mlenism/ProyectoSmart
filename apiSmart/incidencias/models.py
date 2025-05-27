from django.db import models
from apiSmart.shared.models import Falla
from apiSmart.meters.models import Meter

class Incidencia(models.Model):
    incidencia_id = models.CharField(primary_key=True, max_length=255)
    meter_code = models.ForeignKey(Meter, on_delete=models.SET_NULL, db_column='meter_code', null=True)
    fecha_incidencia = models.DateTimeField()# Campo para la fecha en formato yyyy-mm-dd hh-dd-ss
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, db_column='falla_id', null=True) #fallo_id de incidencias referencia a falla_id de Fallas
    encargado = models.CharField(max_length=255)
    img = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'smart_med\".\"final_incidencias'
        managed = False #No manejar migraciones para esta tabla

    def __str__(self):
        str = ("INCIDENCIA\n"
        f"incidencia_id: {self.incidencia_id}\n"
        f"meter_code: {self.meter_code}\n"
        f"fecha_incidencia: {self.fecha_incidencia}\n"
        f"falla: {self.falla}\n"
        f"encargado: {self.encargado}\n"
        f"img: {self.img}")
        return str