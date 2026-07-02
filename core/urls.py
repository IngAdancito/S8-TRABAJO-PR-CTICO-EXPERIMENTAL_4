from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Auth
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),

    # Productos (admin)
    path('productos/admin/', views.producto_list, name='producto_list'),
    path('productos/admin/crear/', views.producto_create, name='producto_create'),
    path('productos/admin/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('productos/admin/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),

    # Productos (catálogo público)
    path('productos/', views.producto_catalogo, name='producto_catalogo'),

    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/crear/', views.cliente_create, name='cliente_create'),
    path('clientes/editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', views.cliente_delete, name='cliente_delete'),

    # Carrito
    path('carrito/', views.carrito_view, name='carrito_view'),
    path('carrito/agregar/<int:pk>/', views.carrito_add, name='carrito_add'),
    path('carrito/eliminar/<int:pk>/', views.carrito_remove, name='carrito_remove'),
    path('carrito/actualizar/<int:pk>/', views.carrito_update, name='carrito_update'),
    path('checkout/', views.checkout, name='checkout'),

    # Pedidos
    path('pedidos/', views.pedido_list, name='pedido_list'),
    path('pedidos/<int:pk>/', views.pedido_detail, name='pedido_detail'),
    path('pedidos/<int:pk>/estado/', views.pedido_update_estado, name='pedido_update_estado'),
]
