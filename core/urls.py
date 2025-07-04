from django.contrib import admin
from django.urls import path
from miapp.views import inicio
from miapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('', inicio, name='inicio'),  
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-carrito/<int:carrito_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/aumentar/<int:carrito_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('carrito/disminuir/<int:carrito_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('pagar/', views.pagar, name='pagar'),
    path('retorno/', views.retorno, name='retorno'),
    path('pago_resultado/', views.retorno, name='retorno'),
    path('logout/', views.logout_view, name='logout'),
    path('historial/', views.historial_admin, name='historial_admin'),
    path('vendedor/', views.panel_vendedor, name='panel_vendedor'),
    path('vendedor/aceptar/<int:pedido_id>/', views.aceptar_pedido, name='aceptar_pedido'),
    path('redirigir_usuario/', views.redirigir_usuario, name='redirigir_usuario'),

]
