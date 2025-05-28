from django.contrib import admin
from .models import Producto, Carrito, Orden, ItemOrden

# Mostrar los productos comprados dentro de cada orden 
class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0
    readonly_fields = ('producto', 'cantidad')

# Personalizar cómo se ve la orden
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'total_gastado')
    readonly_fields = ('total_gastado',)
    inlines = [ItemOrdenInline]
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username',)

    def total_gastado(self, obj):
        total = sum(
            item.producto.precio * item.cantidad
            for item in obj.items.all()
            if item.producto
        )
        return f"${total:,}".replace(",", ".") 
    total_gastado.short_description = 'Total Gastado'

# Registro de modelos
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(Orden, OrdenAdmin)
admin.site.register(ItemOrden)
