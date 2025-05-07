from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito  # ✅ Usa mayúscula en los nombres

def inicio(request):
    productos = Producto.objects.all()  # ✅ Producto con mayúscula
    return render(request, 'miapp/inicio.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)  # ✅ Producto con mayúscula
    Carrito.objects.create(producto=producto)  # ✅ Carrito con mayúscula
    return redirect('ver_carrito')

def ver_carrito(request):
    carrito_items = Carrito.objects.all()  # ✅ Corregido `objects` y variable
    return render(request, 'miapp/carrito.html', {'carrito': carrito_items})

def eliminar_del_carrito(request, carrito_id):
    item = get_object_or_404(Carrito, pk=carrito_id)
    item.delete()
    return redirect('ver_carrito')