from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito  
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login


def inicio(request):
    liberar_stock_expirado()  # Libera productos reservados hace más de 30 minutos
    productos = Producto.objects.all()
    return render(request, 'miapp/inicio.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    if producto.stock > 0:
        producto.stock -= 1
        producto.save()

        item, creado = Carrito.objects.get_or_create(producto=producto)
        if not creado:
            item.cantidad += 1
        item.save()
    else:
        messages.warning(request, f"Lo sentimos, no hay stock de '{producto.nombre}'.")

    return redirect('ver_carrito')


def ver_carrito(request):
    carrito_items = Carrito.objects.all()  
    return render(request, 'miapp/carrito.html', {'carrito': carrito_items})

def eliminar_del_carrito(request, carrito_id):
    item = get_object_or_404(Carrito, pk=carrito_id)
    producto = item.producto

    # Devolver el stock
    producto.stock += item.cantidad
    producto.save()

    item.delete()
    return redirect('ver_carrito')

def liberar_stock_expirado():
    tiempo_limite = timezone.now() - timedelta(minutes=1)
    items_expirados = Carrito.objects.filter(fecha_agregado__lt=tiempo_limite)

    for item in items_expirados:
        producto = item.producto
        producto.stock += item.cantidad
        producto.save()
        item.delete()    
def aumentar_cantidad(request, carrito_id):
    item = get_object_or_404(Carrito, pk=carrito_id)
    producto = item.producto

    if producto.stock > 0:
        item.cantidad += 1
        item.save()

        producto.stock -= 1
        producto.save()
    else:
        messages.warning(request, f"No hay más stock disponible de '{producto.nombre}'.")

    return redirect('ver_carrito')

def disminuir_cantidad(request, carrito_id):
    item = get_object_or_404(Carrito, pk=carrito_id)
    producto = item.producto

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
        producto.stock += 1
        producto.save()
    else:
        # Si solo queda 1, eliminar el ítem completo
        producto.stock += 1
        producto.save()
        item.delete()

    return redirect('ver_carrito')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')  # Redirige a inicio o donde tú quieras
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'miapp/login.html')