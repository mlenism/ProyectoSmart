from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('download-template/', views.DownloadTemplateView.as_view(), name='download_template'),
]

# Incluye las rutas del router
urlpatterns += router.urls