from django.contrib import admin
from .models import Meter, Tapa
from .alarms.models import Alarma
# Register your models here.

admin.site.register(Meter)
admin.site.register(Tapa)
admin.site.register(Alarma)

