from django.contrib import admin
from .models import Producto, Cliente, Pedido, DetallePedido

admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
