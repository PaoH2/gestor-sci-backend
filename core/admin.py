from django.contrib import admin
from .models import Usuario, Producto, Movimiento

# Personalizamos cómo se ven los usuarios
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_staff')
    search_fields = ('email',)

# Personalizamos productos
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'stock_actual', 'costo')
    search_fields = ('sku', 'nombre')
    list_filter = ('fecha_creacion',)

# Personalizamos movimientos
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'get_producto', 'cantidad', 'fecha', 'get_usuario')
    list_filter = ('tipo', 'fecha')

    def get_producto(self, obj):
        return obj.producto.sku
    get_producto.short_description = 'SKU'

    def get_usuario(self, obj):
        return obj.usuario.email if obj.usuario else 'Sin usuario'
    get_usuario.short_description = 'Usuario'

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Movimiento, MovimientoAdmin)