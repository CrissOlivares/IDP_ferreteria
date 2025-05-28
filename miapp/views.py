from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, Orden, ItemOrden
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .transbank_config import get_transaction
import uuid
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout



def logout_view(request):
    logout(request)
    return redirect('inicio')

def retorno(request):
    token = request.GET.get('token_ws')
    if not token:
        messages.error(request, "Token no recibido desde Webpay.")
        return redirect('ver_carrito')

    transaction = get_transaction()
    try:
        response = transaction.commit(token)

        if response['status'] == 'AUTHORIZED':
            carrito_items = Carrito.objects.filter(usuario=request.user)

            orden = Orden.objects.create(usuario=request.user)
            for item in carrito_items:
                ItemOrden.objects.create(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad
                )
            carrito_items.delete()
            messages.success(request, "¡Pago exitoso! Historial guardado.")
        else:
            messages.error(request, "El pago fue rechazado.")
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {e}")
        return redirect('ver_carrito')

    return render(request, 'miapp/pago_resultado.html', {'respuesta': response})

def pagar(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para pagar.")
        return redirect('login')

    carrito_items = Carrito.objects.filter(usuario=request.user)
    if not carrito_items:
        messages.warning(request, "El carrito está vacío.")
        return redirect('ver_carrito')

    total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    buy_order = str(uuid.uuid4())[:26]
    session_id = request.session.session_key or str(uuid.uuid4())[:61]
    return_url = 'http://localhost:8000/retorno/'

    transaction = get_transaction()
    response = transaction.create(buy_order, session_id, total, return_url)

    return redirect(response['url'] + '?token_ws=' + response['token'])

    return redirect(response['url'] + '?token_ws=' + response['token'])
def inicio(request):
    liberar_stock_expirado()  # Libera productos reservados hace más de 30 minutos
    productos = Producto.objects.all()
    return render(request, 'miapp/inicio.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para agregar productos al carrito.")
        return redirect('login')

    if producto.stock > 0:
        producto.stock -= 1
        producto.save()

        item, creado = Carrito.objects.get_or_create(producto=producto, usuario=request.user)
        if not creado:
            item.cantidad += 1
        item.save()
    else:
        messages.warning(request, f"Lo sentimos, no hay stock de '{producto.nombre}'.")

    return redirect('ver_carrito')



def ver_carrito(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para ver tu carrito.")
        return redirect('login')

    carrito_items = Carrito.objects.filter(usuario=request.user)
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha')

    return render(request, 'miapp/carrito.html', {
        'carrito': carrito_items,
        'ordenes': ordenes,
    })
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
            return redirect('/')  
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'miapp/login.html')


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
        else:
            user = User.objects.create_user(username=username, password=password1, email=email)
            login(request, user)  # inicia sesión después de registrarse
            return redirect('inicio')

    return render(request, 'miapp/registro.html')
