from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views 
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('admin/', admin.site.urls),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    # otras rutas que tengas
]
