from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.GatewayCreateView, basename='gateways')

urlpatterns = [
    path('gateways_mysql/', views.GatewayMySqlCreateView.as_view({'get':'list'}), name='gatewaysSql'),
    path('autocomplete-gateway/', views.GatewayAutocompleteView.as_view(), name='gateway-autocomplete'),
    path('autocomplete-gateway-mysql/', views.GatewayAutocompleteMySQLView.as_view({'get':'list'}), name='gateway-autocomplete-mysql'),
    path('logs/<str:equip_id>/', views.EquipmentStatusLogListView.as_view(), name='equipment_status_logs'),
    path('count_gateways_online/', views.OnlineGatewaysCountAPIView.as_view(), name='count_status_online'),
]

# Incluye las rutas del router
urlpatterns += router.urls