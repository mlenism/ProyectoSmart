# urls.py
from django.urls import path, include
from rest_framework import routers
from apiSmart import views
from django.conf import settings
from django.conf.urls.static import static

from .distinctObjects import views as distinctViews

router = routers.DefaultRouter()
#router.register(r'incidencias', views.IncidenciaCreateView, basename='incidencias')
router.register(r'unique-tapaDesc', distinctViews.UniqueTapasListView, basename='unique-tapa')
router.register(r'unique-fallaDesc', distinctViews.UniqueFallasDescListView, basename='unique-falla')
router.register(r'vista-combinada', views.VistaCombinadaCreateView, basename='vista-combinada')

urlpatterns = [
    path('', include(router.urls)),
    path('alarms/', include('apiSmart.alarms.urls')),
    path('incidencias/', include('apiSmart.incidencias.urls')), 
    path('dags/', include('apiSmart.airflow.urls')), #Dags podríoan fallar, revisar
    path('meters/', include('apiSmart.meters.urls')), 
    path('gateways/', include('apiSmart.gateways.urls')), 
    path('files/', include('apiSmart.files.urls')),
    path('unique-creators/', distinctViews.UniqueCreatorListView.as_view(), name='unique-creators'),
    path('unique-status/', distinctViews.UniqueStatusListView.as_view(), name='unique-status'),
    path('unique-falla-type/', distinctViews.UniqueFallaTypeListView.as_view(), name='unique-falla-type'),
    path('autocomplete-combinada/', views.CombinedAutocompleteView.as_view(), name='combined-autocomplete'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)