from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
urlpatterns = [
    path('descriptions/', views.get_descriptions, name='get-user-descriptions'),
    path('logout/', views.logOut, name='logout'),
    path('is-authenticated/', views.is_authenticated, name='is-authenticated'),
    path('register/', views.register, name='register'),
]

# Incluye las rutas del router
urlpatterns += router.urls