from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('<str:dag_id>/dagRuns', views.TriggerDagRunView.as_view(), name='trigger_dag_run'),
    path('dagruns', views.GetDagRuns.as_view(), name='get-variables'),
    path('variables', views.GetVariables.as_view(), name='get-dagruns'),
]

# Incluye las rutas del router
urlpatterns += router.urls