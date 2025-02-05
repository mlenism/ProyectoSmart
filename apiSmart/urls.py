# urls.py
from django.urls import path, include
from rest_framework import routers
from apiSmart import views
from django.conf import settings
from django.conf.urls.static import static
from .tokens.views import CustomTokenObtainPairView, CustomRefreshTokenView

from rest_framework_simplejwt.views import TokenRefreshView #JWT

from .distinctObjects import views as distinctViews

router = routers.DefaultRouter()
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
    path('users/', include('apiSmart.users.urls')),
    path('unique-creators/', distinctViews.UniqueCreatorListView.as_view(), name='unique-creators'),
    path('unique-status/', distinctViews.UniqueStatusListView.as_view(), name='unique-status'),
    path('unique-falla-type/', distinctViews.UniqueFallaTypeListView.as_view(), name='unique-falla-type'),
    path('autocomplete-combinada/', views.CombinedAutocompleteView.as_view(), name='combined-autocomplete'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)