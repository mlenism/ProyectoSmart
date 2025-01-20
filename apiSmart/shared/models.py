from django.db import models 

#Modelo para las fallas referentes a las alarmas
class Falla(models.Model):
    falla_id = models.IntegerField(primary_key=True)
    falla_desc = models.CharField(max_length=255)
    falla_type = models.CharField(max_length=500)

    class Meta:
        db_table = 'smart_med"."final_fallas'
        managed = False