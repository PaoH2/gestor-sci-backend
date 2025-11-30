from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Modelo de Usuario Personalizado
class Usuario(AbstractUser):
    ROLES = (('Superadmin', 'Superadmin'), ('Operador', 'Operador'))
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='Operador')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# 2. Modelo de Producto
class Producto(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    
    # CORREGIDO: Eliminamos el duplicado y dejamos solo una definición
    stock_actual = models.IntegerField(default=0)
    
    # Mantenemos el default en 5 para nuevos productos
    nivel_minimo_stock = models.IntegerField(default=5)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # Para borrado lógico

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

# 3. Modelo de Movimiento
class Movimiento(models.Model):
    TIPOS = (
        ('Entrada', 'Entrada'), 
        ('Salida', 'Salida'), 
        ('Creacion', 'Creacion'), 
        ('Eliminacion', 'Eliminacion')
    )
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nom_prod = self.producto.sku if self.producto else "Producto Eliminado"
        return f"{self.tipo} - {nom_prod} ({self.cantidad})"
    
class Venta(models.Model):
    folio = models.CharField(max_length=50, unique=True) 
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Venta {self.folio} - ${self.total}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.sku}"