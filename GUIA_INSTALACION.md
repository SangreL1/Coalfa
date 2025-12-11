# Guía de Instalación y Configuración

## 📋 Tabla de Contenidos
1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
5. [Configuración para Producción](#configuración-para-producción)
6. [Solución de Problemas](#solución-de-problemas)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

## 🖥️ Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: Versión 3.8 o superior
- **RAM**: 4 GB mínimo
- **Espacio en disco**: 500 MB mínimo

### Requisitos Recomendados
- **Python**: Versión 3.10 o superior
- **RAM**: 8 GB o más
- **Espacio en disco**: 1 GB
- **Procesador**: 2+ núcleos

### Software Requerido
1. **Python 3.8+**
   - Descargar desde [python.org](https://www.python.org/downloads/)
   - Verificar instalación: `python --version`

2. **pip** (gestor de paquetes Python)
   - Viene incluido con Python 3.4+
   - Verificar: `pip --version`

3. **Git** (opcional, para clonar repositorio)
   - Descargar desde [git-scm.com](https://git-scm.com/)

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar o Descargar el Proyecto

#### Opción A: Clonar con Git
```bash
# Clonar el repositorio
git clone <url-del-repositorio>

# Navegar al directorio del proyecto
cd Gestios_Citas_IS
```

#### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del repositorio
2. Extraer el contenido en una carpeta
3. Abrir terminal en la carpeta extraída

### Paso 2: Crear Entorno Virtual

#### Windows
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar que se activó (debería aparecer (venv) al inicio de la línea)
(venv) C:\ruta\al\proyecto>
```

#### macOS/Linux
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar que se activó (debería aparecer (venv) al inicio de la línea)
(venv) usuario@equipo:~/Gestios_Citas_IS$
```

### Paso 3: Instalar Dependencias

```bash
# Instalar Django
pip install django

# Instalar dependencias adicionales (si existen)
pip install -r requirements.txt  # Si el archivo existe

# Verificar instalación
python -m django --version
```

### Paso 4: Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Verificar que la base de datos se creó
ls db.sqlite3  # Debería existir el archivo
```

### Paso 5: Crear Superusuario

```bash
# Crear usuario administrador
python manage.py createsuperuser

# Seguir las instrucciones:
# Username: admin
# Email: admin@ejemplo.com
# Password: (elegir una contraseña segura)
```

### Paso 6: Ejecutar Servidor de Desarrollo

```bash
# Iniciar servidor
python manage.py runserver

# El servidor estará disponible en:
# http://localhost:8000
# http://127.0.0.1:8000
```

### Paso 7: Verificar Instalación

1. Abrir navegador web
2. Ir a `http://localhost:8000`
3. Debería ver la página de inicio del sistema
4. Ir a `http://localhost:8000/admin` para acceder al panel de administración

## ⚙️ Configuración del Entorno

### Variables de Entorno (Opcional)

Crear archivo `.env` en la raíz del proyecto:

```env
# .env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Configuración de Django

El archivo principal de configuración es `Gestios_Citas_IS/settings.py`. Las configuraciones principales son:

```python
# Configuración básica
DEBUG = True  # Cambiar a False en producción
ALLOWED_HOSTS = []  # Agregar dominios en producción
SECRET_KEY = 'django-insecure-...'  # Cambiar en producción

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Agenda',
    'registration',
]

# Base de datos (SQLite por defecto)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🗄️ Configuración de la Base de Datos

### SQLite (Desarrollo - Por Defecto)

No requiere configuración adicional. La base de datos se crea automáticamente en `db.sqlite3`.

### PostgreSQL (Producción Recomendada)

1. **Instalar PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows: Descargar desde postgresql.org
```

2. **Crear base de datos y usuario**
```sql
-- Conectar a PostgreSQL
sudo -u postgres psql

-- Crear base de datos
CREATE DATABASE gestios_citas;

-- Crear usuario
CREATE USER gestios_user WITH PASSWORD 'contraseña_segura';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE gestios_citas TO gestios_user;

-- Salir
\q
```

3. **Configurar Django para PostgreSQL**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gestios_citas',
        'USER': 'gestios_user',
        'PASSWORD': 'contraseña_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. **Instalar adaptador PostgreSQL**
```bash
pip install psycopg2-binary
```

### MySQL (Alternativa)

1. **Instalar MySQL y adaptador**
```bash
pip install mysqlclient
```

2. **Configurar Django para MySQL**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestios_citas',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🏭 Configuración para Producción

### 1. Configuración de Seguridad

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com', 'ip-del-servidor']

# Configuración HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Secret Key segura (generar nueva)
SECRET_KEY = 'generar-nueva-clave-segura-aqui'
```

### 2. Servidor de Archivos Estáticos

```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Configurar servidor web (Nginx ejemplo)
# /etc/nginx/sites-available/gestios_citas
server {
    listen 80;
    server_name tudominio.com;
    
    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }
    
    location /media/ {
        alias /ruta/al/proyecto/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Servidor de Aplicaciones (Gunicorn)

```bash
# Instalar Gunicorn
pip install gunicorn

# Configurar servicio systemd
# /etc/systemd/system/gestios.service
[Unit]
Description=Gunicorn para Gestios Citas
After=network.target

[Service]
User=usuario
Group=www-data
WorkingDirectory=/ruta/al/proyecto
ExecStart=/ruta/al/venv/bin/gunicorn --workers 3 --bind unix:/ruta/al/proyecto/gestios.sock Gestios_Citas_IS.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4. Configuración con Docker (Opcional)

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "Gestios_Citas_IS.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/gestios_citas
    depends_on:
      - db

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=gestios_citas
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password

volumes:
  postgres_data:
```

## 🔧 Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Error: "ModuleNotFoundError: No module named 'django'"
```bash
# Solución: Activar entorno virtual e instalar Django
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install django
```

#### 2. Error: "Database is locked"
```bash
# Solución: Cerrar otras conexiones a la base de datos
# Reiniciar servidor o eliminar archivo db.sqlite3 y recrear migraciones
rm db.sqlite3
python manage.py migrate
```

#### 3. Error: "Port 8000 already in use"
```bash
# Solución: Usar otro puerto
python manage.py runserver 8001

# O matar proceso en puerto 8000
# Linux/macOS:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 4. Error: "Invalid RUT" durante registro
- Verificar formato del RUT (12345678-9)
- Asegurarse que el dígito verificador sea correcto
- Probar con RUT de prueba: 12345678-5

#### 5. Error: "Permission denied" en archivos media
```bash
# Linux/macOS: Dar permisos al directorio media
sudo chmod -R 755 media/
sudo chown -R $USER:www-data media/

# Windows: Verificar permisos de escritura en la carpeta
```

### Verificación del Sistema

Script de verificación `check_system.py`:

```python
# check_system.py
import sys
import django

print("=== Verificación del Sistema ===")
print(f"Python: {sys.version}")
print(f"Django: {django.get_version()}")

try:
    from Agenda.models import validar_rut_chileno
    print("✓ Validador de RUT importado correctamente")
except ImportError as e:
    print(f"✗ Error importando validador: {e}")

print("=== Verificación completada ===")
```

Ejecutar:
```bash
python check_system.py
```

### Testing del Sistema

Para ejecutar las pruebas del sistema:

```bash
# Ejecutar pruebas de Django
python manage.py test

# Ejecutar pruebas específicas de RUT
python tests/test_rut_validation.py
python tests/test_with_real_rut.py

# Ejecutar script de depuración
python tests/debug_rut.py
```

## ❓ Preguntas Frecuentes

### P: ¿Cómo cambio el idioma del sistema?
**R**: Editar `settings.py`:
```python
LANGUAGE_CODE = 'es-cl'  # Español Chile
TIME_ZONE = 'America/Santiago'
```

### P: ¿Cómo agrego más especialidades médicas?
**R**: Desde el panel de administración (`/admin`) o usando el formulario en `/gestion/especialidades/crear/`

### P: ¿Cómo restablezco la contraseña de un usuario?
**R**: 
1. Desde línea de comandos:
```bash
python manage.py changepassword username
```
2. Desde panel de administración Django

### P: ¿Cómo hago backup de la base de datos?
**R**: 
```bash
# SQLite
cp db.sqlite3 db_backup.sqlite3

# PostgreSQL
pg_dump -U usuario gestios_citas > backup.sql

# Django dumpdata
python manage.py dumpdata > backup.json
```

### P: ¿Cómo actualizo el sistema?
**R**: 
```bash
# 1. Hacer backup
cp db.sqlite3 db_backup.sqlite3

# 2. Actualizar código
git pull origin main  # Si usa Git

# 3. Actualizar dependencias
pip install -r requirements.txt --upgrade

# 4. Aplicar migraciones
python manage.py migrate

# 5. Reiniciar servidor
```

### P: ¿Cómo configuro email para recuperación de contraseña?
**R**: En `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña'
```

## 📞 Soporte Técnico

### Canales de Soporte
1. **Documentación**: Revisar esta guía y DOCUMENTACION_TECNICA.md
2. **Issues GitHub**: Reportar bugs en el repositorio
3. **Foro de la comunidad**: [Enlace al foro si existe]

### Información para Reportar Problemas
Al reportar un problema, incluir:
1. Sistema operativo y versión
2. Versión de Python (`python --version`)
3. Versión de Django (`python -m django --version`)
4. Pasos para reproducir el error
5. Mensaje de error completo
6. Capturas de pantalla (si aplica)

### Recursos Adicionales
- [Documentación oficial de Django](https://docs.djangoproject.com/)
- [Tutorial Django en español](https://tutorial.djangogirls.org/es/)
- [Foro de la comunidad Django](https://forum.djangoproject.com/)

---

*Última actualización: Diciembre 2025*  
*Versión de esta guía: 1.0.0*  
*Sistema compatible: Django 5.2.7, Python 3.8+*