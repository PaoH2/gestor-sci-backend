from rest_framework import serializers
from .models import Usuario, Producto, Movimiento
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Venta, DetalleVenta

# --- LOGIN PERSONALIZADO ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'email': self.user.email,
            'role': self.user.role
        }
        data['token'] = data['access'] 
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'role', 'username']

class ProductoSerializer(serializers.ModelSerializer):
    # Mapeamos nombres para coincidir con el Frontend
    ID_Producto = serializers.IntegerField(source='id', read_only=True)
    SKU = serializers.CharField(source='sku')
    Nombre_Producto = serializers.CharField(source='nombre')
    Descripcion = serializers.CharField(source='descripcion', required=False)
    Costo = serializers.DecimalField(source='costo', max_digits=10, decimal_places=2)
    Stock_Actual = serializers.IntegerField(source='stock_actual', read_only=True)
    Nivel_Minimo_Stock = serializers.IntegerField(source='nivel_minimo_stock', required=False)

    class Meta:
        model = Producto
        fields = ['ID_Producto', 'SKU', 'Nombre_Producto', 'Descripcion', 'Costo', 'Stock_Actual', 'Nivel_Minimo_Stock']

class MovimientoSerializer(serializers.ModelSerializer):
    # --- CAMPOS CALCULADOS (Ya los tenías) ---
    Nombre_Producto = serializers.CharField(source='producto.nombre', read_only=True)
    Email_Usuario = serializers.CharField(source='usuario.email', read_only=True)
    SKU = serializers.CharField(source='producto.sku', read_only=True)
    
    # --- CORRECCIÓN: RENOMBRAR CAMPOS PARA ANGULAR ---
    # Mapeamos el campo 'fecha' de la BD al nombre 'Fecha' del JSON
    Fecha = serializers.DateTimeField(source='fecha', read_only=True)
    # Mapeamos 'cantidad' a 'Cantidad'
    Cantidad = serializers.IntegerField(source='cantidad', read_only=True)
    
    # Campo para recibir el SKU al crear (input)
    sku_input = serializers.CharField(write_only=True, required=False) 

    class Meta:
        model = Movimiento
        # IMPORTANTE: En la lista 'fields' usamos los nombres con Mayúscula
        fields = [
            'id', 'tipo', 'Cantidad', 'Fecha', 
            'Nombre_Producto', 'Email_Usuario', 'SKU', 'sku_input'
        ]
        
class DetalleVentaSerializer(serializers.ModelSerializer):
    Nombre_Producto = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'precio_unitario', 'subtotal', 'Nombre_Producto']

class VentaSerializer(serializers.ModelSerializer):
    Usuario = serializers.CharField(source='usuario.email', read_only=True)
    # Incluimos los detalles anidados para poder reimprimir el ticket
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Venta
        fields = ['id', 'folio', 'fecha', 'total', 'Usuario', 'detalles']