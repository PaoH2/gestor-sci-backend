from django.contrib import admin
from .models import Usuario, Categoria, Producto, Movimiento, Venta, DetalleVenta

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'role')
    list_filter = ('role', 'is_staff', 'is_active')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'stock_actual', 'nivel_minimo_stock', 'categoria', 'is_active')
    list_filter = ('categoria', 'is_active')
    search_fields = ('sku', 'nombre')
    list_editable = ('nivel_minimo_stock', 'is_active')

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'producto', 'cantidad', 'usuario', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__sku', 'producto__nombre')
    readonly_fields = ('fecha',)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha', 'total', 'usuario')
    list_filter = ('fecha',)
    search_fields = ('folio',)
    inlines = [DetalleVentaInline]
    readonly_fields = ('folio', 'fecha', 'total', 'usuario')