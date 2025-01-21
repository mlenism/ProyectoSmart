from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.IncidenciaCreateView, basename='incidencias')

urlpatterns = [
    path('conteo-incidencias/', views.ConteoIncidenciasBase.as_view(), name='conteo_incidencias'),
]

# Incluye las rutas del router
urlpatterns += router.urls