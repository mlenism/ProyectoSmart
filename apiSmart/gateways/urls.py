from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.GatewayCreateView, basename='gateways')

urlpatterns = [
    path('gateways_mysql/', views.GatewayMySqlCreateView.as_view({'get':'list'}), name='gatewaysSql'),
    path('autocomplete-gateway/', views.GatewayAutocompleteView.as_view(), name='gateway-autocomplete'),
    path('logs/<str:equip_id>/', views.EquipmentStatusLogListView.as_view(), name='equipment_status_logs'),
]

# Incluye las rutas del router
urlpatterns += router.urls