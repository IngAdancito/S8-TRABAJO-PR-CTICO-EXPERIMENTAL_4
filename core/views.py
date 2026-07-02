from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from .models import Producto, Cliente, Pedido, DetallePedido
from .forms import ProductoForm, ClienteForm, RegistroForm, AgregarCarritoForm


def admin_required(user):
    return user.is_authenticated and user.is_staff


def es_cliente(user):
    return user.is_authenticated and hasattr(user, 'cliente')


# ─── Auth ──────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cliente.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registro exitoso. ¡Bienvenido!')
            return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Dashboard ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_staff:
        total_productos = Producto.objects.count()
        total_clientes = Cliente.objects.count()
        total_pedidos = Pedido.objects.count()
        ingresos = Pedido.objects.filter(estado__in=['pagado', 'enviado', 'entregado']).aggregate(
            total=Sum('total')
        )['total'] or 0
        productos_bajos = Producto.objects.filter(stock__lte=5).count()
        pedidos_recientes = Pedido.objects.select_related('cliente__user').all()[:5]
        return render(request, 'core/dashboard.html', {
            'total_productos': total_productos,
            'total_clientes': total_clientes,
            'total_pedidos': total_pedidos,
            'ingresos': ingresos,
            'productos_bajos': productos_bajos,
            'pedidos_recientes': pedidos_recientes,
            'es_admin': True,
        })
    cliente = request.user.cliente
    pedidos = cliente.pedidos.all()[:5]
    total_gastado = cliente.pedidos.filter(
        estado__in=['pagado', 'enviado', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0
    return render(request, 'core/dashboard.html', {
        'pedidos': pedidos,
        'total_gastado': total_gastado,
        'es_admin': False,
    })


# ─── Productos ─────────────────────────────────────────────────────────────

def producto_catalogo(request):
    productos = Producto.objects.all().order_by('-creado')
    return render(request, 'core/producto_catalogo.html', {'productos': productos})


@user_passes_test(admin_required)
def producto_list(request):
    productos = Producto.objects.all().order_by('-creado')
    return render(request, 'core/producto_list.html', {'productos': productos})


@user_passes_test(admin_required)
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'core/producto_form.html', {'form': form, 'accion': 'Crear'})


@user_passes_test(admin_required)
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'core/producto_form.html', {'form': form, 'accion': 'Editar'})


@user_passes_test(admin_required)
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('producto_list')
    return render(request, 'core/producto_confirm_delete.html', {'producto': producto})


# ─── Clientes ──────────────────────────────────────────────────────────────

@user_passes_test(admin_required)
def cliente_list(request):
    clientes = Cliente.objects.select_related('user').all()
    return render(request, 'core/cliente_list.html', {'clientes': clientes})


@user_passes_test(admin_required)
def cliente_create(request):
    if request.method == 'POST':
        reg_form = RegistroForm(request.POST)
        cli_form = ClienteForm(request.POST)
        if reg_form.is_valid() and cli_form.is_valid():
            user = reg_form.save()
            cliente = cli_form.save(commit=False)
            cliente.user = user
            cliente.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('cliente_list')
    else:
        reg_form = RegistroForm()
        cli_form = ClienteForm()
    return render(request, 'core/cliente_form.html', {
        'reg_form': reg_form, 'cli_form': cli_form, 'accion': 'Crear',
    })


@user_passes_test(admin_required)
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente.objects.select_related('user'), pk=pk)
    if request.method == 'POST':
        cli_form = ClienteForm(request.POST, instance=cliente)
        if cli_form.is_valid():
            cli_form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('cliente_list')
    else:
        cli_form = ClienteForm(instance=cliente)
    return render(request, 'core/cliente_form.html', {
        'cli_form': cli_form, 'cliente': cliente, 'accion': 'Editar',
    })


@user_passes_test(admin_required)
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.user.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('cliente_list')
    return render(request, 'core/cliente_confirm_delete.html', {'cliente': cliente})


# ─── Carrito (sesión) ──────────────────────────────────────────────────────

@login_required
def carrito_view(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for prod_id, data in carrito.items():
        prod = get_object_or_404(Producto, pk=prod_id)
        subtotal = prod.precio * data['cantidad']
        items.append({
            'producto': prod,
            'cantidad': data['cantidad'],
            'subtotal': subtotal,
        })
        total += subtotal
    return render(request, 'core/carrito.html', {'items': items, 'total': total})


@login_required
def carrito_add(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AgregarCarritoForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            if cantidad > producto.stock:
                messages.error(request, f'Solo hay {producto.stock} unidades disponibles.')
                return redirect('producto_catalogo')
            carrito = request.session.get('carrito', {})
            str_pk = str(pk)
            if str_pk in carrito:
                nueva_cant = carrito[str_pk]['cantidad'] + cantidad
                if nueva_cant > producto.stock:
                    messages.error(request, 'No hay suficiente stock.')
                    return redirect('producto_catalogo')
                carrito[str_pk]['cantidad'] = nueva_cant
            else:
                carrito[str_pk] = {'cantidad': cantidad}
            request.session['carrito'] = carrito
            messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('producto_catalogo')


@login_required
def carrito_remove(request, pk):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(pk), None)
    request.session['carrito'] = carrito
    messages.info(request, 'Producto eliminado del carrito.')
    return redirect('carrito_view')


@login_required
def carrito_update(request, pk):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad < 1:
            carrito.pop(str(pk), None)
        else:
            producto = get_object_or_404(Producto, pk=pk)
            if cantidad > producto.stock:
                messages.error(request, f'Solo hay {producto.stock} unidades disponibles.')
                return redirect('carrito_view')
            carrito[str(pk)] = {'cantidad': cantidad}
        request.session['carrito'] = carrito
    return redirect('carrito_view')


@login_required
def checkout(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'El carrito está vacío.')
        return redirect('producto_catalogo')
    cliente = request.user.cliente
    total = 0
    detalles = []
    for prod_id, data in carrito.items():
        prod = get_object_or_404(Producto, pk=prod_id)
        if data['cantidad'] > prod.stock:
            messages.error(request, f'Stock insuficiente para {prod.nombre}.')
            return redirect('carrito_view')
        subtotal = prod.precio * data['cantidad']
        total += subtotal
        detalles.append({
            'producto': prod,
            'cantidad': data['cantidad'],
            'precio_unitario': prod.precio,
        })
    if request.method == 'POST':
        pedido = Pedido.objects.create(cliente=cliente, total=total)
        for det in detalles:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=det['producto'],
                cantidad=det['cantidad'],
                precio_unitario=det['precio_unitario'],
            )
            det['producto'].stock -= det['cantidad']
            det['producto'].save()
        request.session['carrito'] = {}
        messages.success(request, 'Pedido realizado con éxito.')
        return redirect('pedido_list')
    return render(request, 'core/checkout.html', {
        'items': detalles, 'total': total,
        'cliente': cliente,
    })


# ─── Pedidos ───────────────────────────────────────────────────────────────

@login_required
def pedido_list(request):
    if request.user.is_staff:
        pedidos = Pedido.objects.select_related('cliente__user').all()
    else:
        pedidos = request.user.cliente.pedidos.select_related('cliente__user').all()
    return render(request, 'core/pedido_list.html', {'pedidos': pedidos})


@login_required
def pedido_detail(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related('cliente__user').prefetch_related('detalles__producto'),
        pk=pk,
    )
    if not request.user.is_staff and pedido.cliente.user != request.user:
        messages.error(request, 'No tienes permiso para ver este pedido.')
        return redirect('dashboard')
    return render(request, 'core/pedido_detail.html', {'pedido': pedido})


@user_passes_test(admin_required)
def pedido_update_estado(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado actualizado a {pedido.get_estado_display()}.')
    return redirect('pedido_detail', pk=pk)
