from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from rrhh.models import Empleado
from inventario.models import Lote, TareaBodega
import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            rut = form.cleaned_data["rut"]
            password = form.cleaned_data["password"]
            user = authenticate(request, rut=rut, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "RUT o contraseña incorrectos.")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="/login/")
def dashboard(request):
    context = {}

    if request.user.rol in ("RRHH", "ADMIN"):
        total_empleados = Empleado.objects.count()
        en_vacaciones = Empleado.objects.filter(estado="VACACIONES").count()
        con_licencia = Empleado.objects.filter(estado="LICENCIA").count()
        finiquitados = Empleado.objects.filter(estado="FINIQUITADO").count()
        context.update({
            "total_empleados": total_empleados,
            "en_vacaciones": en_vacaciones,
            "con_licencia": con_licencia,
            "finiquitados": finiquitados,
        })

    if request.user.rol in ("OPERACIONAL", "ADMIN"):
        hoy = datetime.date.today()
        pronto = hoy + datetime.timedelta(days=7)
        lotes_bodega = Lote.objects.filter(ubicacion_actual="BODEGA", estado="ACTIVO").count()
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__lte=pronto,
            fecha_vencimiento__gte=hoy,
            estado="ACTIVO"
        ).count()
        context.update({
            "lotes_bodega": lotes_bodega,
            "lotes_por_vencer": lotes_por_vencer,
        })

    # Tareas (visibles para todos los roles, pero solo las propias)
    tareas = TareaBodega.objects.filter(usuario=request.user)
    context.update({
        "tareas": tareas,
        "tareas_pendientes": tareas.filter(completada=False).count(),
    })

    # Badge de solicitudes pendientes para admin
    if request.user.rol == "ADMIN":
        from .models import Usuario
        context["solicitudes_count"] = Usuario.objects.filter(solicitud_pendiente=True).count()

    return render(request, "coalfa/dashboard.html", context)


# ── Registro público ────────────────────────────────────────────────────────────

def registro_view(request):
    from .models import Usuario
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None
    if request.method == "POST":
        p = request.POST
        rut = p.get("rut", "").strip().upper().replace(".", "").replace(" ", "")
        nombre = p.get("nombre", "").strip()
        apellido = p.get("apellido", "").strip()
        password = p.get("password", "")
        password2 = p.get("password2", "")

        if not all([rut, nombre, apellido, password]):
            error = "Todos los campos son obligatorios."
        elif password != password2:
            error = "Las contraseñas no coinciden."
        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif Usuario.objects.filter(rut=rut).exists():
            error = "Ya existe una cuenta con ese RUT."
        else:
            Usuario.objects.create_user(
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                password=password,
                is_active=False,
                solicitud_pendiente=True,
            )
            return render(request, "registro_enviado.html")

    return render(request, "registro.html", {"error": error})


# ── Panel admin: solicitudes ────────────────────────────────────────────────────

def _admin_required(view_func):
    """Decorador simple para vistas solo-admin."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.rol != "ADMIN":
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


@_admin_required
def admin_solicitudes(request):
    from .models import Usuario
    pendientes = Usuario.objects.filter(solicitud_pendiente=True).order_by("date_joined")
    rol_choices = Usuario.ROL_CHOICES
    return render(request, "admin/solicitudes.html", {
        "pendientes": pendientes,
        "rol_choices": rol_choices,
    })


@_admin_required
def admin_aprobar(request, pk):
    from .models import Usuario
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, pk=pk, solicitud_pendiente=True)
        rol = request.POST.get("rol", "RRHH")
        usuario.rol = rol
        usuario.is_active = True
        usuario.solicitud_pendiente = False
        usuario.save()
        messages.success(request, f"✅ {usuario.get_full_name()} activado como {usuario.get_rol_display()}.")
    return redirect("admin_solicitudes")


@_admin_required
def admin_rechazar(request, pk):
    from .models import Usuario
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, pk=pk, solicitud_pendiente=True)
        nombre = usuario.get_full_name()
        usuario.delete()
        messages.success(request, f"Solicitud de {nombre} rechazada y eliminada.")
    return redirect("admin_solicitudes")
