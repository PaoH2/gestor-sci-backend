from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Modelo de Usuario Personalizado
class Usuario(AbstractUser):
    # Hereda username, password, etc.
    ROLES = (('Superadmin', 'Superadmin'), ('Operador', 'Operador'))
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='Operador')

    # Usaremos el email para hacer login en lugar del username
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
    stock_actual = models.IntegerField(default=0)
    nivel_minimo_stock = models.IntegerField(default=5)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    stock_actual = models.IntegerField(default=0)
    # NUEVO CAMPO:
    is_active = models.BooleanField(default=True) # Para borrado lógico

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

# 3. Modelo de Movimiento
class Movimiento(models.Model):
    # Agregamos 'Creacion' y 'Eliminacion' a las opciones
    TIPOS = (
        ('Entrada', 'Entrada'), 
        ('Salida', 'Salida'), 
        ('Creacion', 'Creacion'), 
        ('Eliminacion', 'Eliminacion')
    )
    
    # Aumentamos max_length a 20 para que quepan las nuevas palabras
    tipo = models.CharField(max_length=20, choices=TIPOS)
    
    # IMPORTANTE: Cambiamos on_delete a SET_NULL.
    # Si borras el producto, el historial se queda, pero el campo producto se pone en NULL.
    # Así no pierdes el registro de que "algo" pasó.
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Manejo seguro en caso de que el producto ya no exista
        nom_prod = self.producto.sku if self.producto else "Producto Eliminado"
        return f"{self.tipo} - {nom_prod} ({self.cantidad})"
    
class Venta(models.Model):
    # Generamos un folio único (ej. V-1698203000)
    folio = models.CharField(max_length=50, unique=True) 
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Venta {self.folio} - ${self.total}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # PROTECT: No borrar producto si ya se vendió
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio al momento de la venta
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.sku}"