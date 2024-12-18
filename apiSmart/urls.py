# urls.py
from django.urls import path, include
from rest_framework import routers
from apiSmart import views
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'incidencias', views.IncidenciaCreateView, basename='incidencias')
router.register(r'gateways', views.GatewayCreateView, basename='gateways')
router.register(r'gateways_mysql', views.GatewayMySqlCreateView, basename='gatewaysSql')
router.register(r'meters', views.MeterViewSet)
router.register(r'alarms', views.AlarmViewSet)
router.register(r'meters-empty', views.MeterEmptyViewSet, basename='meter-empty')
router.register(r'unique-tapaDesc', views.UniqueTapasListView, basename='unique-tapa')
router.register(r'unique-fallaDesc', views.UniqueFallasDescListView, basename='unique-falla')
router.register(r'vista-combinada', views.VistaCombinadaCreateView, basename='vista-combinada')

urlpatterns = [
    path('', include(router.urls)),
    path('dags/<str:dag_id>/dagRuns', views.TriggerDagRunView.as_view(), name='trigger_dag_run'),
    path('dags/dagruns', views.GetDagRuns.as_view(), name='get-variables'),
    path('dags/variables', views.GetVariables.as_view(), name='get-dagruns'),
    path('unique-creators/', views.UniqueCreatorListView.as_view(), name='unique-creators'),
    path('unique-status/', views.UniqueStatusListView.as_view(), name='unique-status'),
    path('unique-falla-type/', views.UniqueFallaTypeListView.as_view(), name='unique-falla-type'),
    path('autocomplete/', views.MeterAutocompleteView.as_view(), name='meter-autocomplete'),
    path('autocomplete-gateway/', views.GatewayAutocompleteView.as_view(), name='gateway-autocomplete'),
    path('autocomplete-alarma/', views.AlarmaAutocompleteView.as_view(), name='alarma-autocomplete'),
    path('autocomplete-combinada/', views.CombinedAutocompleteView.as_view(), name='combined-autocomplete'),
    path('incidencias-alarmas/', views.AlarmasIncidenciasView.as_view(), name='incidencias-alarmas'),
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('exclusivos-por-gateway/', views.MedidoresExclusivosPorGatewayAPIView.as_view(), name='medidores_exclusivos_por_gateway'),
    path('no-exclusivos-por-gateway/', views.MedidoresNoExclusivosPorGatewayAPIView.as_view(), name='medidores_no_exclusivos_por_gateway'),
    path('logs/<str:equip_id>/', views.EquipmentStatusLogListView.as_view(), name='equipment_status_logs'),
    path('download-template/', views.DownloadTemplateView.as_view(), name='download_template'),
    path('conteo-incidencias/', views.ConteoIncidenciasBase.as_view(), name='conteo_incidencias'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)