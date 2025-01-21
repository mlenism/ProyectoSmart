from django.db import models 

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