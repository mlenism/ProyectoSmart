from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('tipo-lectura/<str:meter_id>/', views.MeterStatusView.as_view(), name='medidores_exclusivos_por_gateway'),
    path('ultima-lectura/<str:meter_id>/', views.LastReadingView.as_view(), name='ultima_lectura'),
]

# Incluye las rutas del router
urlpatterns += router.urls