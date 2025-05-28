from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito  
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .transbank_config import get_transaction
import uuid
def retorno(request):
    token = request.GET.get('token_ws')

    # ✅ Validación inmediata
    if not token:
        messages.error(request, "Token no recibido desde Webpay.")
        return redirect('ver_carrito')

    transaction = get_transaction()
    try:
        response = transaction.commit(token)

        if response['status'] == 'AUTHORIZED':
            Carrito.objects.all().delete()
            messages.success(request, "¡Pago exitoso!")
        else:
            messages.error(request, "El pago fue rechazado.")
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {e}")
        return redirect('ver_carrito')

    return render(request, 'miapp/pago_resultado.html', {'respuesta': response})

    return render(request, 'miapp/pago_resultado.html', {'respuesta': response})
def pagar(request):
    carrito_items = Carrito.objects.all()

    if not carrito_items:
        messages.warning(request, "El carrito está vacío.")
        return redirect('ver_carrito')

    # Calcular el total
    total = sum(item.producto.precio * item.cantidad for item in carrito_items)

    # Crear orden y sesión única
    buy_order = str(uuid.uuid4())[:26]  # Orden única, limitada a 26 caracteres
    session_id = request.session.session_key or str(uuid.uuid4())[:61]
    return_url = 'http://localhost:8000/retorno/'  # Cambia esto a tu dominio en producción

    transaction = get_transaction()
    response = transaction.create(buy_order, session_id, total, return_url)

    # Opcional: guardar temporalmente los datos de la compra en sesión o base de datos si necesitas mostrarlos luego

    return redirect(response['url'] + '?token_ws=' + response['token'])
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
