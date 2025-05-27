from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    # otras rutas que tengas
]
