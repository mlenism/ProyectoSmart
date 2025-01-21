from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.AlarmViewSet, basename='alarmas')

urlpatterns = [
    path('autocomplete-alarma/', views.AlarmaAutocompleteView.as_view(), name='alarma-autocomplete'),
]

# Incluye las rutas del router
urlpatterns += router.urls