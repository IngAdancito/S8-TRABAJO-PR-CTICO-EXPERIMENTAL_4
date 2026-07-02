from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from .models import Producto, Cliente, Pedido, DetallePedido
from .views import producto_catalogo


class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Test Producto",
            descripcion="Descripción de prueba",
            precio=10000,
            stock=5,
        )

    def test_producto_creation(self):
        self.assertEqual(self.producto.nombre, "Test Producto")
        self.assertEqual(self.producto.precio, 10000)
        self.assertEqual(self.producto.stock, 5)

    def test_producto_str(self):
        self.assertEqual(str(self.producto), "Test Producto")

    def test_producto_stock_bajo(self):
        self.assertLessEqual(self.producto.stock, 5)


class ClienteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.cliente = Cliente.objects.create(
            user=self.user,
            telefono="+56 9 1234 5678",
            direccion="Calle Falsa 123",
        )

    def test_cliente_creation(self):
        self.assertEqual(self.cliente.telefono, "+56 9 1234 5678")
        self.assertEqual(self.cliente.user.username, "testuser")

    def test_cliente_str(self):
        self.assertIn(self.cliente.user.username, str(self.cliente))


class PedidoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cliente1", password="pass123")
        self.cliente = Cliente.objects.create(user=self.user)
        self.producto = Producto.objects.create(
            nombre="Laptop", precio=500000, stock=10
        )
        self.pedido = Pedido.objects.create(cliente=self.cliente, total=500000)
        self.detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=1,
            precio_unitario=500000,
        )

    def test_pedido_creation(self):
        self.assertEqual(self.pedido.estado, "pendiente")
        self.assertEqual(self.pedido.total, 500000)

    def test_pedido_str(self):
        self.assertIn(str(self.pedido.id), str(self.pedido))

    def test_detalle_subtotal(self):
        self.assertEqual(self.detalle.subtotal(), 500000)

    def test_pedido_detalles_count(self):
        self.assertEqual(self.pedido.detalles.count(), 1)

    def test_pedido_estados_validos(self):
        estados_validos = ["pendiente", "pagado", "enviado", "entregado", "cancelado"]
        self.assertIn(self.pedido.estado, estados_validos)


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        Producto.objects.create(
            nombre="Monitor", precio=200000, stock=3
        )

    def test_catalogo_status(self):
        request = self.factory.get("/productos/")
        response = producto_catalogo(request)
        self.assertEqual(response.status_code, 200)
