from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    CategoriaViewSet,
    UsuarioViewSet, 
    ProductoViewSet, 
    MovimientoViewSet, 
    DashboardView, 
    CustomLoginView, 
    RegisterView, 
    VentaViewSet 
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'ventas', VentaViewSet, basename='ventas')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('api/login', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('api/register', RegisterView.as_view(), name='register'),
    # Dashboard
    path('api/dashboard/metrics', DashboardView.as_view()),

    # Movimientos
    path('api/movimientos', MovimientoViewSet.as_view({'get': 'list'})),
    path('api/movimientos/entrada', MovimientoViewSet.as_view({'post': 'entrada'})),
    path('api/movimientos/salida', MovimientoViewSet.as_view({'post': 'salida'})),

    # Ventas (POS)
    ##path('api/ventas/registrar', VentaViewSet.as_view({'post': 'registrar'})),

    # Router automático
    path('api/', include(router.urls)),
]