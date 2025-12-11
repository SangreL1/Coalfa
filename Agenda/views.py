from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import (
    Medico,
    Paciente,
    FichaMedica,
    VisitaAtencion,
    Medicamentos,
    Examenes,
    Especialidad,
)
from .forms import (
    PacienteForm,
    VisitaAtencionForm,
    MedicoForm,
    FichaMedicaForm,
    UserForm,
    MedicamentosForm,
    ExamenesForm,
    EspecialidadForm,
)


# --- VERIFICADORES DE ROL ---
def es_medico(user):
    return user.is_authenticated and hasattr(user, "medico")


def es_admin(user):
    return user.is_authenticated and user.is_staff


# --- VISTAS GENERALES ---
def home(request):
    return render(request, "Agenda/home.html")


# --- AREA CLÍNICA (SOLO MÉDICOS) ---


@login_required
@user_passes_test(es_medico)
def dashboard_medico(request):
    medico = request.user.medico
    # Atenciones del médico
    atenciones = VisitaAtencion.objects.filter(medico=medico).order_by(
        "-fecha_atencion"
    )

    # Búsqueda de atenciones por nombre o RUT
    query = request.GET.get("q")
    if query:
        atenciones = VisitaAtencion.objects.filter(
            Q(medico=medico)
            & (
                Q(paciente__user__first_name__icontains=query)
                | Q(paciente__user__last_name__icontains=query)
                | Q(paciente__rut__icontains=query)
            )
        ).order_by("-fecha_atencion")

    return render(
        request, "Agenda/dashboard_medico.html", {"citas": atenciones, "query": query}
    )


@login_required
@user_passes_test(es_medico)
def buscar_paciente(request):
    query = request.GET.get("rut")
    paciente = None

    if query:
        paciente = Paciente.objects.filter(rut=query).first()
        if not paciente:
            messages.warning(
                request, f"No se encontró paciente con RUT {query}. Puede registrarlo."
            )
            return redirect("registrar_paciente")
        else:
            return redirect("ver_ficha", paciente_id=paciente.id)

    return render(request, "Agenda/buscar_paciente.html")


@login_required
@user_passes_test(es_medico)
def registrar_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data["rut"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]

            # Verificar si ya existe un usuario con ese RUT
            if User.objects.filter(username=rut).exists():
                messages.error(request, f"Ya existe un usuario con el RUT {rut}.")
                return render(request, "Agenda/registrar_paciente.html", {"form": form})

            # Crear usuario asociado al paciente
            user = User.objects.create_user(
                username=rut,
                email=email,
                password=rut,  # Contraseña inicial = RUT
                first_name=first_name,
                last_name=last_name,
            )

            paciente = form.save(commit=False)
            paciente.user = user
            paciente.save()

            # Crear ficha vacía automáticamente
            FichaMedica.objects.create(paciente=paciente)
            messages.success(
                request, "Paciente registrado y ficha creada exitosamente."
            )
            return redirect("ver_ficha", paciente_id=paciente.id)
    else:
        form = PacienteForm()
    return render(request, "Agenda/registrar_paciente.html", {"form": form})


@login_required
@user_passes_test(es_medico)
def ver_ficha(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    # Validar si tiene ficha, si no, crearla (seguridad)
    ficha, created = FichaMedica.objects.get_or_create(paciente=paciente)

    # Si la ficha está vacía (sin antecedentes), redirigir a editar
    if not any(
        [
            ficha.alergias,
            ficha.enfermedades_cronicas,
            ficha.medicamentos,
            ficha.antecedentes_familiares,
        ]
    ):
        messages.info(request, "Por favor complete la ficha médica del paciente.")
        return redirect("editar_ficha", paciente_id=paciente.id)

    visitas = VisitaAtencion.objects.filter(paciente=paciente).order_by(
        "-fecha_atencion"
    )

    return render(
        request,
        "Agenda/ver_ficha.html",
        {"paciente": paciente, "visitas": visitas, "ficha": ficha},
    )


@login_required
@user_passes_test(es_medico)
def crear_atencion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    # Asegurar que existe ficha
    ficha, created = FichaMedica.objects.get_or_create(paciente=paciente)

    medico = request.user.medico

    if request.method == "POST":
        form = VisitaAtencionForm(request.POST, medico=medico)
        if form.is_valid():
            atencion = form.save(commit=False)
            # Asociar directamente el paciente y médico a la atención
            atencion.paciente = paciente
            atencion.medico = medico
            atencion.save()
            form.save_m2m()  # Guardar relaciones ManyToMany (medicamentos y examenes)
            messages.success(request, "Atención registrada correctamente.")
            return redirect("ver_ficha", paciente_id=paciente.id)
    else:
        form = VisitaAtencionForm(medico=medico)

    return render(
        request, "Agenda/crear_atencion.html", {"form": form, "paciente": paciente}
    )


@login_required
@user_passes_test(es_medico)
def editar_ficha(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    ficha, created = FichaMedica.objects.get_or_create(paciente=paciente)

    if request.method == "POST":
        form = FichaMedicaForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, "Ficha médica actualizada correctamente.")
            return redirect("ver_ficha", paciente_id=paciente.id)
    else:
        form = FichaMedicaForm(instance=ficha)

    return render(
        request, "Agenda/editar_ficha.html", {"form": form, "paciente": paciente}
    )


# --- AREA ADMINISTRATIVA (SOLO ADMIN) ---


@login_required
@user_passes_test(es_admin)
def lista_medicos(request):
    medicos = Medico.objects.all()
    return render(request, "Agenda/medicos.html", {"medicos": medicos})


@login_required
@user_passes_test(es_admin)
def crear_medico(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        medico_form = MedicoForm(request.POST, request.FILES)

        # Lo asignaremos manualmente después de crear el usuario
        if "user" in medico_form.fields:
            del medico_form.fields["user"]

        if user_form.is_valid() and medico_form.is_valid():
            # Crear usuario
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            # Crear médico vinculado
            medico = medico_form.save(commit=False)
            medico.user = user

            # Verificar si ya existe un médico con el mismo RUT antes de intentar guardar
            rut_usuario = user.username  # El RUT se guarda en el username del usuario
            if Medico.objects.filter(rut=rut_usuario).exists():
                messages.error(
                    request, f"Ya existe un médico con el RUT {rut_usuario}."
                )
                # Limpiar el campo user del formulario para evitar problemas de validación
                if "user" in medico_form.fields:
                    del medico_form.fields["user"]
                return render(
                    request,
                    "Agenda/create_medico_form.html",
                    {"user_form": user_form, "form": medico_form},
                )
            else:
                medico.rut = rut_usuario  # Asignar el RUT del usuario al médico
                try:
                    medico.save()
                    medico_form.save_m2m()  # Guardar especialidades
                    messages.success(
                        request, "Médico y usuario registrados exitosamente."
                    )
                    return redirect("lista_medicos")
                except Exception as e:
                    # Manejar otros errores inesperados
                    messages.error(request, "Ocurrió un error al registrar el médico.")
                    # Limpiar el campo user del formulario para evitar problemas de validación
                    if "user" in medico_form.fields:
                        del medico_form.fields["user"]
                    return render(
                        request,
                        "Agenda/create_medico_form.html",
                        {"user_form": user_form, "form": medico_form},
                    )
    else:
        user_form = UserForm()
        medico_form = MedicoForm()
        # Eliminamos el campo 'user' para que no aparezca en el template
        if "user" in medico_form.fields:
            del medico_form.fields["user"]

    return render(
        request,
        "Agenda/create_medico_form.html",
        {"user_form": user_form, "form": medico_form},
    )


@login_required
@user_passes_test(es_admin)
def update_medico(request, pk):
    medico = get_object_or_404(Medico, pk=pk)
    if request.method == "POST":
        form = MedicoForm(request.POST, request.FILES, instance=medico)
        if form.is_valid():
            # Verificar si hay un campo rut en el formulario
            # El RUT se maneja a través del username del usuario
            form.save()
            messages.success(request, "Médico actualizado correctamente.")
            return redirect("lista_medicos")
    else:
        form = MedicoForm(instance=medico)
    return render(
        request, "Agenda/update_medico.html", {"form": form, "medico": medico}
    )


@login_required
@user_passes_test(es_admin)
def delete_medico(request, pk):
    medico = get_object_or_404(Medico, pk=pk)
    if request.method == "POST":
        medico.delete()
        messages.success(request, "Médico eliminado correctamente.")
        return redirect("lista_medicos")
    return render(request, "Agenda/delete_medico.html", {"medico": medico})


# --- GESTIÓN DE MEDICAMENTOS (SOLO ADMIN) ---


@login_required
@user_passes_test(es_admin)
def lista_medicamentos(request):
    medicamentos = Medicamentos.objects.all()
    return render(request, "Agenda/medicamentos.html", {"medicamentos": medicamentos})


@login_required
@user_passes_test(es_admin)
def crear_medicamento(request):
    if request.method == "POST":
        form = MedicamentosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicamento creado correctamente.")
            return redirect("lista_medicamentos")
    else:
        form = MedicamentosForm()
    return render(request, "Agenda/create_medicamento.html", {"form": form})


@login_required
@user_passes_test(es_admin)
def update_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamentos, pk=pk)
    if request.method == "POST":
        form = MedicamentosForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicamento actualizado correctamente.")
            return redirect("lista_medicamentos")
    else:
        form = MedicamentosForm(instance=medicamento)
    return render(
        request,
        "Agenda/update_medicamento.html",
        {"form": form, "medicamento": medicamento},
    )


@login_required
@user_passes_test(es_admin)
def delete_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamentos, pk=pk)
    if request.method == "POST":
        medicamento.delete()
        messages.success(request, "Medicamento eliminado correctamente.")
        return redirect("lista_medicamentos")
    return render(
        request, "Agenda/delete_medicamento.html", {"medicamento": medicamento}
    )


# --- GESTIÓN DE EXAMENES (SOLO ADMIN) ---


@login_required
@user_passes_test(es_admin)
def lista_examenes(request):
    examenes = Examenes.objects.all()
    return render(request, "Agenda/examenes.html", {"examenes": examenes})


@login_required
@user_passes_test(es_admin)
def crear_examen(request):
    if request.method == "POST":
        form = ExamenesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen creado correctamente.")
            return redirect("lista_examenes")
    else:
        form = ExamenesForm()
    return render(request, "Agenda/create_examen.html", {"form": form})


@login_required
@user_passes_test(es_admin)
def update_examen(request, pk):
    examen = get_object_or_404(Examenes, pk=pk)
    if request.method == "POST":
        form = ExamenesForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen actualizado correctamente.")
            return redirect("lista_examenes")
    else:
        form = ExamenesForm(instance=examen)
    return render(
        request, "Agenda/update_examen.html", {"form": form, "examen": examen}
    )


@login_required
@user_passes_test(es_admin)
def delete_examen(request, pk):
    examen = get_object_or_404(Examenes, pk=pk)
    if request.method == "POST":
        examen.delete()
        messages.success(request, "Examen eliminado correctamente.")
        return redirect("lista_examenes")
    return render(request, "Agenda/delete_examen.html", {"examen": examen})


# Vista para buscar medicamentos
def buscar_medicamentos(request):
    query = request.GET.get("q", "")
    medicamentos = []
    if query:
        medicamentos = Medicamentos.objects.filter(nombre__icontains=query)
    else:
        medicamentos = Medicamentos.objects.all()[
            :10
        ]  # Mostrar 10 medicamentos como ejemplo

    # Preparar respuesta JSON
    results = []
    for med in medicamentos:
        results.append(
            {"id": med.id, "nombre": med.nombre, "descripcion": med.descripcion}
        )

    from django.http import JsonResponse

    return JsonResponse({"medicamentos": results})


# --- GESTIÓN DE ESPECIALIDADES (SOLO ADMIN) ---


@login_required
@user_passes_test(es_admin)
def lista_especialidades(request):
    especialidades = Especialidad.objects.all()
    return render(
        request, "Agenda/especialidades.html", {"especialidades": especialidades}
    )


@login_required
@user_passes_test(es_admin)
def crear_especialidad(request):
    if request.method == "POST":
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Especialidad creada correctamente.")
            return redirect("lista_especialidades")
    else:
        form = EspecialidadForm()
    return render(request, "Agenda/create_especialidad.html", {"form": form})


@login_required
@user_passes_test(es_admin)
def update_especialidad(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == "POST":
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, "Especialidad actualizada correctamente.")
            return redirect("lista_especialidades")
    else:
        form = EspecialidadForm(instance=especialidad)
    return render(
        request,
        "Agenda/update_especialidad.html",
        {"form": form, "especialidad": especialidad},
    )


@login_required
@user_passes_test(es_admin)
def delete_especialidad(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == "POST":
        especialidad.delete()
        messages.success(request, "Especialidad eliminada correctamente.")
        return redirect("lista_especialidades")
    return render(
        request, "Agenda/delete_especialidad.html", {"especialidad": especialidad}
    )
