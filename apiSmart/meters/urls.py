from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.MeterViewSet, basename='meters')
router.register(r'meters-empty', views.MeterEmptyViewSet, basename='meter-empty')

urlpatterns = [
    path('exclusivos-por-gateway/', views.MedidoresExclusivosPorGatewayAPIView.as_view(), name='medidores_exclusivos_por_gateway'),
    path('no-exclusivos-por-gateway/', views.MedidoresNoExclusivosPorGatewayAPIView.as_view(), name='medidores_no_exclusivos_por_gateway'),
    path('autocomplete/', views.MeterAutocompleteView.as_view(), name='meter-autocomplete'),
    path('multiple-status/', views.MultiMeterStatusAndReadingView.as_view(), name='multiple-status'),
]

# Incluye las rutas del router
urlpatterns += router.urls