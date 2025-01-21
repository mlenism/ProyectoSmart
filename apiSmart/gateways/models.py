from django.db import models

##Modelo de MySQL
class EquipStatus(models.Model):
    equip_id = models.CharField(max_length=255)
    online_status = models.IntegerField()
    last_update_time = models.DateTimeField()

    class Meta:
        managed = False  # Evita que Django intente gestionar esta tabla (si ya existe)
        db_table = 'as_equip_status'


class EquipmentStatusLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    equip_id = models.CharField(max_length=255)
    status_time = models.DateTimeField()
    online_status = models.BooleanField()

    class Meta:
        db_table = 'as_equip_status_logs'
##----------------------------------------------------------------

# Creación del Modelo Alarmas donde se verán los registros de las fallas
class Gateway(models.Model):
    gateway_id = models.CharField(primary_key=True, max_length=255)
    latitude = models.DecimalField(max_digits=20, decimal_places=17)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)
    status = models.CharField(max_length=30)
    service_center = models.CharField(max_length=255)

    class Meta:
        db_table = 'smart_med\".\"stg3_gateways'
        managed = False #No manejar migraciones para esta tabla