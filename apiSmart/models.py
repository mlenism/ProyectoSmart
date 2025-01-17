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

#Modelo para las fallas referentes a las alarmas
class Falla(models.Model):
    falla_id = models.IntegerField(primary_key=True)
    falla_desc = models.CharField(max_length=255)
    falla_type = models.CharField(max_length=500)

    class Meta:
        db_table = 'smart_med"."final_fallas'
        managed = False

#Modelo para las tapas referentes a los medidores
class Tapa(models.Model):
    tapa_id = models.IntegerField(primary_key=True)
    tapa_desc = models.CharField(max_length=255)

    class Meta:
        db_table = 'smart_med"."final_tapas'
        managed = False

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

# Creación del Modelo Alarmas donde se verán los registros de las fallas
class Alarma(models.Model):
    alarm_pk = models.PositiveBigIntegerField(primary_key=True)
    alarm_id = models.CharField(max_length=25)
    meter_code = models.CharField(max_length=25)
    alarm_time_id = models.IntegerField()  # Campo para la fecha en formato YYYYMMDD
    alarm_timestamp_id = models.IntegerField()    # Campo para la hora en formato HHMMSS
    recv_time_id = models.IntegerField()  # Campo para la fecha en formato YYYYMMDD
    recv_timestamp_id = models.IntegerField()    # Campo para la hora en formato HHMMSS
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, db_column='fallo_id', null=True) #fallo_id de alarmas referencia a falla_id de Fallas

    class Meta:
        db_table = 'smart_med\".\"final_alarmas'
        managed = False #No manejar migraciones para esta tabla

# Creación del Modelo Alarmas donde se verán los registros de las fallas
class Incidencia(models.Model):
    incidencia_id = models.CharField(primary_key=True, max_length=255)
    meter_code = models.CharField(max_length=25)
    fecha_incidencia = models.DateTimeField()# Campo para la fecha en formato yyyy-mm-dd hh-dd-ss
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, db_column='falla_id', null=True) #fallo_id de incidencias referencia a falla_id de Fallas
    encargado = models.CharField(max_length=255)
    img = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'smart_med\".\"final_incidencias'
        managed = False #No manejar migraciones para esta tabla

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
