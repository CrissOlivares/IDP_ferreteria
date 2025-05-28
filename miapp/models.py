from django.db import models
from django.contrib.auth.models import User  # Agrega esta línea

# Definición de la tabla productos
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.IntegerField()
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

# Definición de la tabla carrito
class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ← ESTA LÍNEA

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

