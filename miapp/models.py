from django.db import models

# Definición de la tabla productos
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.IntegerField()  # Solo acepta valores enteros


    def __str__(self):
        return self.nombre

# Definición de la tabla carrito
class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)  # Guarda solo la fecha de creación

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
