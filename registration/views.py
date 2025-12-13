from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegistroPacienteForm


# Create your views here.
def loginView(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}!")

            # Lógica de Redirección según Rol (HU-01)
            if user.is_staff:
                return redirect("/")  # Admin -> Home
            elif hasattr(user, "medico"):
                return redirect("/")  # Médico -> Home
            else:
                return redirect("home")  # Home
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "registration/login.html", {"form": form})


def logoutView(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente")
    return redirect("home")


def registerView(request):
    if request.method == "POST":
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registro exitoso. Por favor inicia sesión.")
            return redirect("login")
    else:
        form = RegistroPacienteForm()

    return render(request, "registration/register.html", {"form": form})
