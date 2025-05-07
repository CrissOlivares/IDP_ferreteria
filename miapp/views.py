from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito  
from django.contrib import messages

def inicio(request):
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