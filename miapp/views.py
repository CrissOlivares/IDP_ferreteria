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
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import Pedido
from django.contrib.auth.decorators import user_passes_test
# miapp/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required



@login_required
def redirigir_usuario(request):
    print("Grupos del usuario:", request.user.groups.all())  # ← línea clave
    if request.user.groups.filter(name='Vendedores').exists():
        print("Redirigiendo al panel del vendedor")
        return redirect('panel_vendedor')
    else:
        print("Redirigiendo al home")
        return redirect('inicio')


def logout_view(request):
    logout(request)
    return redirect('inicio')

@never_cache
def retorno(request):
    print(f"Session key: {request.session.session_key}")
    print(f"User ID en sesión: {request.session.get('usuario_pago_id')}")
    token = request.GET.get('token_ws')
    if not token:
        messages.error(request, "Token no recibido desde Webpay.")
        return redirect('ver_carrito')

    # recurpar la sesion 
    user_id = request.session.get('usuario_pago_id')
    if not user_id:
        messages.error(request, "No se pudo verificar al usuario para completar la compra.")
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    transaction = get_transaction()
    try:
        response = transaction.commit(token)

        if response['status'] == 'AUTHORIZED':
            carrito_items = Carrito.objects.filter(usuario=user)

            orden = Orden.objects.create(usuario=user)
            for item in carrito_items:
                ItemOrden.objects.create(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad
                )
                 # Crear pedido para el panel del vendedor
                Pedido.objects.create(
                    producto=item.producto,
                    cantidad=item.cantidad,
                    cliente=user,
                    aceptado=False  
                )
            carrito_items.delete()
            messages.success(request, "¡Pago exitoso! Historial guardado.")
        else:
            messages.error(request, "El pago fue rechazado.")
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {e}")
        return redirect('ver_carrito')

    return render(request, 'miapp/pago_resultado.html', {'respuesta': response})
@never_cache
def pagar(request):
    print(f"Session key antes: {request.session.session_key}")

    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para pagar.")
        return redirect('login')

    carrito_items = Carrito.objects.filter(usuario=request.user)
    if not carrito_items:
        messages.warning(request, "El carrito está vacío.")
        return redirect('ver_carrito')

    total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    buy_order = str(uuid.uuid4())[:26]

    # Django crea y registre la sesión
    if not request.session.session_key:
        request.session.save()

    session_id = request.session.session_key
    return_url = 'http://localhost:8000/retorno/'

    request.session['usuario_pago_id'] = request.user.id

    transaction = get_transaction()
    response = transaction.create(buy_order, session_id, total, return_url)

    return redirect(response['url'] + '?token_ws=' + response['token'])
@never_cache 
def inicio(request):
    liberar_stock_expirado()  
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


@never_cache
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
@never_cache
def login_view(request):
    logout(request)  
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('redirigir_usuario')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'miapp/login.html')
@never_cache
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
def es_vendedor(user):
    return user.groups.filter(name='Vendedores').exists()


@user_passes_test(es_vendedor)
def panel_vendedor(request):
    pedidos = Pedido.objects.filter(vendedor__isnull=True)
    return render(request, 'miapp/panel_vendedor.html', {'pedidos': pedidos})


@user_passes_test(es_vendedor)
def aceptar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.vendedor = request.user
    pedido.aceptado = True
    pedido.save()
    return redirect('panel_vendedor')
    
@never_cache
@staff_member_required
def historial_admin(request):
    ordenes = Orden.objects.all().order_by('-fecha')
    return render(request, 'miapp/historial_admin.html', {'ordenes': ordenes})