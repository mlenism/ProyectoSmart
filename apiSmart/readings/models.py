from django.db import models

class FinalHechos(models.Model):
    gateway_id = models.CharField(max_length=16, null=True, blank=True)
    eui = models.CharField(max_length=16, null=True, blank=True)
    meter_id = models.CharField(max_length=16, db_index=True)  # 🔹 Index para mejorar rendimiento
    real_volume = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    recv_time_id = models.IntegerField(db_index=True)  # 🔹 Formato YYYYMMDD (indexado para eficiencia)
    recv_ts_id = models.IntegerField(null=True, blank=True)
    dept_code = models.CharField(max_length=11, null=True, blank=True)
    seq = models.BigIntegerField(null=True, blank=True)
    freq = models.DecimalField(max_digits=11, decimal_places=1, null=True, blank=True)
    sf = models.CharField(max_length=16, null=True, blank=True)
    rssi = models.CharField(max_length=8, null=True, blank=True)
    lnsr = models.DecimalField(max_digits=11, decimal_places=1, null=True, blank=True)
    meter_time = models.IntegerField(null=True, blank=True)
    row_num = models.IntegerField(null=True, blank=True)
    lectura_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'smart_med\".\"final_hechos' #Nombre real de la tabla en la base de datos
        indexes = [
            models.Index(fields=["meter_id"]),
            models.Index(fields=["recv_time_id"]),
        ]
        managed = False

    def __str__(self):
        return f"Meter {self.meter_id} - {self.recv_time_id}"
