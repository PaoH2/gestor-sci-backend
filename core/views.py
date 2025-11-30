from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum, F, Count, Q
from django.db import transaction
import time
from .serializers import VentaSerializer

# Importamos los modelos
from .models import Usuario, Producto, Movimiento, Venta, DetalleVenta
# Importamos los serializadores
from .serializers import (
    UsuarioSerializer, 
    ProductoSerializer, 
    MovimientoSerializer, 
    MyTokenObtainPairSerializer
)

# --- PERMISOS ---
from rest_framework.permissions import BasePermission
class IsSuperadmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Superadmin'

# --- LOGIN ---
class CustomLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'Operador')
        
        if Usuario.objects.filter(email=email).exists():
            return Response({'error': 'El email ya está registrado.'}, status=409)
        
        user = Usuario.objects.create_user(username=email, email=email, password=password, role=role)
        return Response({'message': 'Usuario registrado exitosamente.'}, status=201)

# --- USUARIOS ---
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSuperadmin()]
        return [permissions.IsAuthenticated()]

class ProductoViewSet(viewsets.ModelViewSet):
    # Traemos solo los activos por defecto
    queryset = Producto.objects.filter(is_active=True)
    serializer_class = ProductoSerializer
    ##permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'sku'
    
    def get_permissions(self):
        # Si la acción es 'destroy' (borrar), exigimos ser Superadmin
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsSuperadmin()]
        
        # Para todo lo demás (ver, crear, editar), solo pedimos estar logueado
        return [permissions.IsAuthenticated()]
    # --- NUEVO MÉTODO CREATE (Resurrección) ---
    def create(self, request, *args, **kwargs):
        sku = request.data.get('SKU')
        
        # 1. Buscamos si existe un producto "muerto" con ese SKU
        producto_inactivo = Producto.objects.filter(sku=sku, is_active=False).first()

        if producto_inactivo:
            # 2. Si existe, lo revivimos
            producto_inactivo.is_active = True
            
            # Actualizamos sus datos con los nuevos que mandaste (Nombre, Costo, etc.)
            serializer = self.get_serializer(producto_inactivo, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Registramos el evento en el historial como una "Reactivación" o Creación
            Movimiento.objects.create(
                tipo='Creacion', # Lo marcamos como creación para el usuario
                producto=producto_inactivo,
                cantidad=producto_inactivo.stock_actual,
                usuario=request.user
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 3. Si no existe, creamos uno nuevo normalmente
        return super().create(request, *args, **kwargs)

    # --- MÉTODOS QUE YA TENÍAS (Mantén estos igual) ---
    def perform_create(self, serializer):
        producto_nuevo = serializer.save()
        Movimiento.objects.create(
            tipo='Creacion',
            producto=producto_nuevo,
            cantidad=producto_nuevo.stock_actual,
            usuario=self.request.user
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        Movimiento.objects.create(
            tipo='Eliminacion',
            producto=instance,
            cantidad=instance.stock_actual,
            usuario=self.request.user
        )

# --- MOVIMIENTOS ---
class MovimientoViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.role == 'Superadmin':
            queryset = Movimiento.objects.all().order_by('-fecha')
        else:
            queryset = Movimiento.objects.filter(usuario=user).order_by('-fecha')
        serializer = MovimientoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def entrada(self, request):
        return self._registrar_movimiento(request, 'Entrada')

    @action(detail=False, methods=['post'])
    def salida(self, request):
        return self._registrar_movimiento(request, 'Salida')

    def _registrar_movimiento(self, request, tipo):
        sku = request.data.get('SKU')
        cantidad = int(request.data.get('Cantidad', 0))
        
        if cantidad <= 0:
            return Response({'error': 'Cantidad debe ser positiva.'}, status=400)

        try:
            with transaction.atomic():
                producto = Producto.objects.select_for_update().get(sku=sku)
                
                if tipo == 'Salida':
                    if producto.stock_actual < cantidad:
                        return Response({
                            'error': 'Stock insuficiente.',
                            'stockDisponible': producto.stock_actual
                        }, status=400)
                    producto.stock_actual -= cantidad
                else:
                    producto.stock_actual += cantidad
                
                producto.save()
                
                Movimiento.objects.create(
                    tipo=tipo, producto=producto, cantidad=cantidad, usuario=request.user
                )
                
                bajo_stock = False
                if producto.nivel_minimo_stock > 0 and producto.stock_actual <= producto.nivel_minimo_stock:
                    bajo_stock = True

                return Response({
                    'message': f'{tipo} registrada exitosamente.',
                    'productoActualizado': ProductoSerializer(producto).data,
                    'bajoStock': bajo_stock
                }, status=201)

        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=404)

# --- VENTAS (POS) ---
class VentaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venta.objects.all().order_by('-fecha') # Las más recientes primero
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def registrar(self, request):
        items = request.data.get('items', [])
        total_recibido = request.data.get('total')

        if not items:
            return Response({'error': 'El carrito está vacío.'}, status=400)

        try:
            with transaction.atomic():
                folio_nuevo = f"V-{int(time.time())}"
                venta = Venta.objects.create(
                    folio=folio_nuevo,
                    total=total_recibido,
                    usuario=request.user
                )

                for item in items:
                    prod_id = item.get('id_producto')
                    cantidad = int(item.get('cantidad'))
                    precio = item.get('precio')

                    producto_db = Producto.objects.select_for_update().get(id=prod_id)

                    if producto_db.stock_actual < cantidad:
                        raise Exception(f"Stock insuficiente para {producto_db.nombre}")

                    producto_db.stock_actual -= cantidad
                    producto_db.save()

                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto_db,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=float(precio) * cantidad
                    )
                    
                    # Registro en Kardex (Movimientos)
                    Movimiento.objects.create(
                        tipo='Salida',
                        producto=producto_db,
                        cantidad=cantidad,
                        usuario=request.user
                    )

                return Response({'message': 'Venta registrada', 'folio': folio_nuevo}, status=201)

        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

# --- DASHBOARD ---
class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_productos = Producto.objects.count()
        valor_inventario = sum([p.stock_actual * p.costo for p in Producto.objects.all()])
        total_stock = Producto.objects.aggregate(Sum('stock_actual'))['stock_actual__sum'] or 0
        
        productos_bajo_stock = Producto.objects.filter(
            nivel_minimo_stock__gt=0, 
            stock_actual__lte=F('nivel_minimo_stock')
        ).count()

        total_entradas = Movimiento.objects.filter(tipo='Entrada').count()
        total_salidas = Movimiento.objects.filter(tipo='Salida').count()

        return Response({
            'totalProductos': total_productos,
            'totalStock': total_stock,
            'valorInventario': valor_inventario,
            'productosBajoStock': productos_bajo_stock,
            'totalEntradas': total_entradas,
            'totalSalidas': total_salidas
        })