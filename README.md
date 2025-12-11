# Gestión de Citas Médicas - Sistema de Gestión Clínica

Sistema web desarrollado en Django para la gestión de pacientes, médicos y atenciones médicas en un entorno clínico.

## 📋 Descripción del Proyecto

Sistema de gestión clínica que permite:
- **Gestión de pacientes**: Registro, búsqueda y administración de fichas médicas
- **Gestión de médicos**: Administración de profesionales médicos con especialidades
- **Atenciones médicas**: Registro de consultas, diagnósticos y tratamientos
- **Gestión de medicamentos y exámenes**: Catálogo de medicamentos y exámenes médicos
- **Validación de RUT chileno**: Sistema robusto de validación de RUT con dígito verificador

## 🏗️ Arquitectura del Sistema

### Tecnologías Utilizadas
- **Backend**: Django 5.2.7
- **Base de datos**: SQLite3 (desarrollo)
- **Frontend**: HTML5, CSS3, Bootstrap
- **Autenticación**: Sistema de usuarios Django con roles personalizados
- **Validación**: Validación de RUT chileno con algoritmo módulo 11

### Estructura del Proyecto
```
Gestios_Citas_IS/
├── Agenda/                    # Aplicación principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Vistas y lógica de negocio
│   ├── forms.py              # Formularios Django
│   ├── urls.py               # Rutas de la aplicación
│   └── templates/Agenda/     # Plantillas HTML
├── registration/             # Aplicación de autenticación
├── Gestios_Citas_IS/         # Configuración del proyecto
├── media/                    # Archivos multimedia subidos
└── db.sqlite3                # Base de datos SQLite
```

## 👥 Roles del Sistema

### 1. **Administrador**
- Gestión completa de médicos
- Administración de medicamentos y exámenes
- Gestión de especialidades médicas
- Supervisión del sistema

### 2. **Médico**
- Dashboard personalizado
- Búsqueda y registro de pacientes
- Visualización y edición de fichas médicas
- Registro de atenciones médicas
- Prescripción de medicamentos y exámenes

### 3. **Paciente**
- Registro en el sistema
- Acceso a información básica
- Visualización de historial médico

## 📊 Modelos de Datos Principales

### Paciente
- RUT (validado)
- Datos personales (nombre, fecha nacimiento, sexo)
- Información de contacto
- Ficha médica asociada

### Médico
- RUT (validado)
- Especialidades (relación ManyToMany)
- Horario laboral
- Foto profesional

### Ficha Médica
- Alergias
- Enfermedades crónicas
- Medicamentos habituales
- Antecedentes familiares

### Visita Atención
- Paciente y médico asociados
- Especialidad de la consulta
- Anamnesis y diagnóstico
- Medicamentos prescritos
- Exámenes solicitados

## 🔐 Sistema de Autenticación

### Validación de RUT Chileno
El sistema implementa un validador robusto de RUT chileno que:
- Acepta múltiples formatos (12345678-9, 12.345.678-9, 123456789)
- Valida el dígito verificador usando algoritmo módulo 11
- Normaliza el formato a estándar (12345678-9)
- Maneja correctamente el dígito 'K'

### Flujo de Autenticación
1. **Registro**: Los pacientes se registran con su RUT como username
2. **Login**: Sistema redirige según rol (admin, médico, paciente)
3. **Contraseña inicial**: Para pacientes, la contraseña inicial es su RUT

## 🚀 Funcionalidades Principales

### Para Médicos
- **Dashboard médico**: Vista personalizada con atenciones recientes
- **Búsqueda de pacientes**: Por RUT con validación en tiempo real
- **Registro de pacientes**: Formulario completo con validación
- **Ficha médica**: Visualización y edición de antecedentes
- **Atenciones**: Registro completo de consultas con medicamentos y exámenes

### Para Administradores
- **Gestión de médicos**: CRUD completo de profesionales
- **Catálogo de medicamentos**: Administración de medicamentos disponibles
- **Catálogo de exámenes**: Administración de exámenes médicos
- **Especialidades**: Gestión de especialidades médicas

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes Python)
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Gestios_Citas_IS
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install django
```

4. **Configurar base de datos**
```bash
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

7. **Acceder al sistema**
- URL: http://localhost:8000
- Admin: http://localhost:8000/admin

## 📁 Estructura de Archivos

### Archivos Clave
- `Agenda/models.py`: Define todos los modelos del sistema
- `Agenda/views.py`: Contiene la lógica de negocio y vistas
- `Agenda/forms.py`: Formularios Django con validación personalizada
- `Agenda/urls.py`: Configuración de rutas de la aplicación
- `Gestios_Citas_IS/settings.py`: Configuración del proyecto Django

### Plantillas HTML
Las plantillas están organizadas por funcionalidad:
- `templates/Agenda/`: Plantillas de la aplicación principal
- `templates/registration/`: Plantillas de autenticación

## 🔧 Configuración de Desarrollo

### Variables de Entorno
El proyecto usa configuración por defecto de Django. Para producción:
- Cambiar `DEBUG = False`
- Configurar `ALLOWED_HOSTS`
- Usar base de datos PostgreSQL/MySQL
- Configurar `SECRET_KEY` segura

### Base de Datos
- **Desarrollo**: SQLite3 (db.sqlite3)
- **Producción**: PostgreSQL o MySQL recomendados

### Archivos Multimedia
- Configuración en `settings.py`: `MEDIA_URL` y `MEDIA_ROOT`
- Los archivos se almacenan en el directorio `media/`

## 🧪 Testing

El proyecto incluye scripts de prueba organizados en la carpeta `tests/`:
- `tests/test_rut_validation.py`: Pruebas unitarias del validador de RUT
- `tests/test_with_real_rut.py`: Pruebas con RUT reales
- `tests/debug_rut.py`: Script de depuración
- `tests/test_restricciones.py`: Pruebas de restricciones del sistema

Para ejecutar pruebas:
```bash
# Ejecutar pruebas de Django
python manage.py test Agenda

# Ejecutar pruebas específicas de RUT
python tests/test_rut_validation.py
python tests/test_with_real_rut.py
```

## 📈 Flujos de Trabajo

### Flujo Médico
1. Login como médico
2. Acceder al dashboard
3. Buscar paciente por RUT
4. Ver/editar ficha médica
5. Registrar nueva atención
6. Prescribir medicamentos/exámenes

### Flujo Administrativo
1. Login como administrador
2. Gestionar médicos (CRUD)
3. Administrar catálogos (medicamentos, exámenes, especialidades)
4. Supervisar sistema

## 🔒 Seguridad

### Características de Seguridad
- Validación de RUT en backend y frontend
- Protección CSRF habilitada
- Autenticación por roles
- Contraseñas hasheadas
- Sanitización de inputs

### Validaciones Implementadas
- RUT chileno válido
- Fechas no futuras
- Formato de email
- Unicidad de RUT
- Permisos por rol

## 🤝 Contribución

### Guía de Contribución
1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Convenciones de Código
- Seguir convenciones PEP 8 para Python
- Comentar código complejo
- Usar nombres descriptivos en inglés
- Mantener consistencia con el código existente

## 📄 Licencia

Este proyecto está desarrollado para fines educativos como parte de un proyecto de Ingeniería de Software.

## 📞 Soporte

Para reportar bugs o solicitar características:
1. Revisar issues existentes
2. Crear nuevo issue con descripción detallada
3. Incluir pasos para reproducir el problema

---

**Desarrollado por**: Equipo de Ingeniería de Software  
**Versión**: 1.0.0  
**Última actualización**: Diciembre 2025# centro_medico_san_lucas
