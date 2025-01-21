from django.contrib import admin
from .meters.models import Meter
from .shared.models import Tapa
from .alarms.models import Alarma
# Register your models here.

admin.site.register(Meter)
admin.site.register(Tapa)
admin.site.register(Alarma)

