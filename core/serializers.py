from rest_framework import serializers
from .models import Categoria, Usuario, Producto, Movimiento
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Venta, DetalleVenta

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

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    Nombre_Categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
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
        fields = [
            'ID_Producto', 'SKU', 'Nombre_Producto', 'Descripcion', 'Costo', 
            'Stock_Actual', 'Nivel_Minimo_Stock', 'Nombre_Categoria', 'categoria_id'
        ]
        
    def create(self, validated_data):
        categoria_id = validated_data.pop('categoria_id', None)
        if categoria_id:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                validated_data['categoria'] = categoria
            except Categoria.DoesNotExist:
                # Opcional: Levantar una excepción o ignorar si el ID no es válido
                pass
        return super().create(validated_data)

    def update(self, instance, validated_data):
        categoria_id = validated_data.pop('categoria_id', None)
        if categoria_id is not None:
            if categoria_id == 0: # O algún valor que tu frontend envíe para "sin categoría"
                validated_data['categoria'] = None
            else:
                try:
                    categoria = Categoria.objects.get(id=categoria_id)
                    validated_data['categoria'] = categoria
                except Categoria.DoesNotExist:
                    raise serializers.ValidationError({"categoria_id": "La categoría no existe."})

        return super().update(instance, validated_data)

class MovimientoSerializer(serializers.ModelSerializer):
    Nombre_Producto = serializers.CharField(source='producto.nombre', read_only=True)
    Email_Usuario = serializers.CharField(source='usuario.email', read_only=True)
    SKU = serializers.CharField(source='producto.sku', read_only=True)
    Fecha = serializers.DateTimeField(source='fecha', read_only=True)

    Cantidad = serializers.IntegerField(source='cantidad', read_only=True)

    sku_input = serializers.CharField(write_only=True, required=False) 

    class Meta:
        model = Movimiento
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