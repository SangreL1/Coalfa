import os
import django
import sys
from datetime import datetime

# Setup Django
sys.path.append(r'c:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings')
django.setup()

from rrhh.models import Empleado

def parse_date(date_str):
    if not date_str or date_str == '-' or date_str == 'nan':
        return None
    try:
        # Expected format: DD-MM-YYYY or DD/MM/YYYY
        date_str = date_str.replace('/', '-')
        return datetime.strptime(date_str, '%d-%m-%Y').date()
    except Exception:
        return None

# Data extracted from the image
# This is a sample subset to demonstrate the process. I will process the full data if needed.
# Fields: NOMBRE, RUT, CARGO, F NACIMIENTO, NACIONALIDAD, TELEFONO, DIRECCION, ESTADO CIVIL, CORREO ELECTRONICO, F CONTRA, 1° ANEXO, 2° ANEXO, TURNO, HORARIO, EN CASO URGENCIA, TELEFONO, OBSERVACIONES

employee_data = [
    {
        "nombre": "AGUIRRE CRUZ FRANCISCA", "rut": "022.531.026-6", "cargo": "AUXILIAR SERVICIO DE CASINO",
        "f_nac": "19-10-1997", "nac": "BOLIVIANA", "tel": "942646671", "dir": "CALLE TARAPACA 415", 
        "est_civil": "S", "email": "franaguirrecruz@gmail.com", "f_contra": "14-06-2023",
        "anexo1": None, "anexo2": None, "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "MARLENE FLORES", "emerg_tel": "957913385", "obs": ""
    },
    {
        "nombre": "ALEGRIA PONCE SARAI", "rut": "022.251.520-7", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "15-02-1980", "nac": "BOLIVIANA", "tel": "936994793", "dir": "ANTOFAGASTA 2420", 
        "est_civil": "S", "email": "sarai.80@hotmail.com", "f_contra": "29-02-2024",
        "anexo1": "28-02-2024", "anexo2": None, "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "", "emerg_tel": "", "obs": ""
    },
    {
        "nombre": "AYALA ZARATE ELIAS FERNANDO", "rut": "014.122.378-5", "cargo": "CONDUCTOR Y OPERADOR DE ALIMENTACION",
        "f_nac": "14-12-1979", "nac": "CHILENA", "tel": "987483842", "dir": "AVDA ABDE RAHI 1411 VILLA EL SOL", 
        "est_civil": "C", "email": "f_fer_f7@hotmail.con", "f_contra": "11-05-2023",
        "anexo1": "11-03-2024", "anexo2": "10-04-2025", "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "ROSA AYALA", "emerg_tel": "948615844", "obs": ""
    },
    {
        "nombre": "BISA LAZARO, VERONICA MAGDALENA", "rut": "017.018.140-1", "cargo": "AUXILIAR DE COCINA",
        "f_nac": "09-02-1988", "nac": "BOLIVIANA", "tel": "937401491", "dir": "PUERTO SECO MANZANA 12 SITIO 9", 
        "est_civil": "S", "email": "veronica.bisal@gmail.com", "f_contra": "02-11-2022",
        "anexo1": "01-02-2024", "anexo2": "10-02-2024", "turno": "6x1", "horario": "15:00 a 23:00",
        "emerg_nom": "SALVADOR ESCOBAR", "emerg_tel": "941412560", "obs": ""
    },
    {
        "nombre": "CABEZAS CABEZAS CRISTIAN FERNANDO", "rut": "017.653.031-1", "cargo": "CONDUCTOR Y FLETE DE FLETA",
        "f_nac": "25-06-1991", "nac": "CHILENA", "tel": "934333814", "dir": "LOS GRANADOS 14143", 
        "est_civil": "S", "email": "fernando33814@gmail.com", "f_contra": "10-07-2023",
        "anexo1": "10-02-2024", "anexo2": None, "turno": "5x2", "horario": "10:00 a 20:00",
        "emerg_nom": "LINA GARCIA MOLINA", "emerg_tel": "993510006", "obs": ""
    },
    {
        "nombre": "CALCINA QUISPE EDITH", "rut": "023.633.542-5", "cargo": "MAESTRA DE REPOSTERIA",
        "f_nac": "28-11-1981", "nac": "BOLIVIANA", "tel": "981245782", "dir": "PEÑUELAS 12771", 
        "est_civil": "S", "email": "ediche-q@hotmail.com", "f_contra": "21-03-2023",
        "anexo1": "20-04-2024", "anexo2": "20-04-2024", "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "HUMBERTO FLORES", "emerg_tel": "957864705", "obs": ""
    },
    {
        "nombre": "CALPA CANO ESTER CRISTINA", "rut": "022.844.640-k", "cargo": "AUXILIAR SERVICIO DE CASINO",
        "f_nac": "20-11-1990", "nac": "BOLIVIANA", "tel": "984126734", "dir": "PASAJE ISABEL LA CATOLICA 2660", 
        "est_civil": "S", "email": "cristina.cris.cal@gmail.com", "f_contra": "10-10-2023",
        "anexo1": None, "anexo2": None, "turno": "7x7", "horario": "10:00 a 22:00",
        "emerg_nom": "JULIA CALPA", "emerg_tel": "956647964", "obs": ""
    },
    {
        "nombre": "CAMPUSANO GALLI VIRGINIA", "rut": "007.873.393-2", "cargo": "MAESTRA DE COCINA",
        "f_nac": "15-09-1958", "nac": "CHILENA", "tel": "964741366", "dir": "PASAJE EL ORO 3143", 
        "est_civil": "S", "email": "virgi.campusano.1958@gmail.com", "f_contra": "26-03-2021",
        "anexo1": "26-06-2023", "anexo2": "23-01-2024", "turno": "7x7", "horario": "10:00 a 22:00",
        "emerg_nom": "HELEN CAMPUSANO", "emerg_tel": "996129811", "obs": ""
    },
    {
        "nombre": "CARVAJAL ELGUETA DANITZA PAMELA", "rut": "018.423.537-k", "cargo": "AUXILIAR SERVICIO DE CASINO",
        "f_nac": "18-03-1992", "nac": "CHILENA", "tel": "934255013", "dir": "PASAJE SANTOS DUMONT 1450", 
        "est_civil": "S", "email": "danitzacarvajalel@gmail.com", "f_contra": "14-06-2023",
        "anexo1": "29-04-2024", "anexo2": "28-04-2025", "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "LIDIA CARVAJAL", "emerg_tel": "932145311", "obs": ""
    },
    {
        "nombre": "CASTILLO RONDAN DERLY RUBY EUGENIA", "rut": "022.657.822-k", "cargo": "AUXILIAR DE COCINA",
        "f_nac": "30-08-1988", "nac": "COLOMBIANA", "tel": "957102650", "dir": "AV ARGENTINA 4352", 
        "est_civil": "S", "email": "derly.rubi.castillo@gmail.com", "f_contra": "21-12-2021",
        "anexo1": None, "anexo2": None, "turno": "7x7", "horario": "10:00 a 22:00",
        "emerg_nom": "JHON ANDRES CUESTA CASTILLO", "emerg_tel": "965903250", "obs": ""
    },
    {
        "nombre": "CASTILLO TIRADO CLAUDIA HAYDEE", "rut": "025.435.158-3", "cargo": "SUPERVISOR DE CASINO",
        "f_nac": "22-03-1996", "nac": "CHILENA", "tel": "952643531", "dir": "CANAVERALES 4142", 
        "est_civil": "S", "email": "claudia.castillo23@hotmail.com", "f_contra": "04-03-2024",
        "anexo1": "04-03-2024", "anexo2": None, "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "", "emerg_tel": "", "obs": ""
    },
    {
        "nombre": "CASTRO MONTENEGRO MIGUEL FRANCISCO", "rut": "018.775.549-8", "cargo": "AYUDANTE DE COCINA",
        "f_nac": "02-11-1990", "nac": "CHILENA", "tel": "944510515", "dir": "PASAJE RIO JANEIRO 126", 
        "est_civil": "S", "email": "miguecastrocm1@gmail.com", "f_contra": "01-08-2023",
        "anexo1": "01-08-2024", "anexo2": "01-07-2024", "turno": "7x7", "horario": "13:00 a 01:00",
        "emerg_nom": "VERONICA", "emerg_tel": "", "obs": ""
    },
    {
        "nombre": "COAQUIRA ANDIA LUCIA MARIA", "rut": "025.820.701-0", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "12-04-1997", "nac": "CHILENA", "tel": "952507824", "dir": "PSJE TARAPACA NORTE 2149", 
        "est_civil": "S", "email": "luciacoaquira@gmail.com", "f_contra": "01-03-2024",
        "anexo1": "01-03-2024", "anexo2": None, "turno": "5x2", "horario": "11:00 a 21:00",
        "emerg_nom": "JULIA COAQUIRA", "emerg_tel": "978131432", "obs": ""
    },
    {
        "nombre": "COLLAO DELGADO ERIKA NILSA", "rut": "014.288.641-9", "cargo": "JEFA DE PRODUCCION",
        "f_nac": "01-08-1979", "nac": "CHILENA", "tel": "946274641", "dir": "CLARIN DE LA SELVA 1037", 
        "est_civil": "S", "email": "erikacollao.1979@gmail.com", "f_contra": "11-03-2021",
        "anexo1": "11-03-2021", "anexo2": "31-07-2021", "turno": "7x7", "horario": "7:00 a 19:00",
        "emerg_nom": "ANAI COLLAO DELGADO", "emerg_tel": "932128987", "obs": ""
    },
    {
        "nombre": "CUELLO ALARCON ELINER", "rut": "026.349.721-6", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "25-09-1990", "nac": "COLOMBIANA", "tel": "974653541", "dir": "ASHELMAN 350", 
        "est_civil": "S", "email": "elinerccuello@gmail.com", "f_contra": "04-03-2025",
        "anexo1": "03-10-2023", "anexo2": None, "turno": "7x7", "horario": "13:00 a 01:00",
        "emerg_nom": "ABIAHUEL CUELLO", "emerg_tel": "948810056", "obs": ""
    },
    {
        "nombre": "DIEGUEZ ATAYA MARIA MAGDALENA", "rut": "023.704.915-k", "cargo": "GERENTE AUDITORIA INTERNA DE PROSESO",
        "f_nac": "11-04-1985", "nac": "CHILENA", "tel": "974351341", "dir": "MANDETINA S/N SAN JOSE DE ALGARROBO VALPARAISO", 
        "est_civil": "S", "email": "mariadieguezfernandez@gmail.com", "f_contra": "11-03-2025",
        "anexo1": None, "anexo2": None, "turno": "5x2", "horario": "1:00 a 16:30",
        "emerg_nom": "", "emerg_tel": "", "obs": ""
    },
    {
        "nombre": "ESCATE RETAMAL FERNANDO", "rut": "010.512.693-2", "cargo": "ADMINISTRADOR DE CASINO",
        "f_nac": "12-01-1979", "nac": "CHILENA", "tel": "942205517", "dir": "PEDRO LEON GALLO 805 SAN CARLOS", 
        "est_civil": "S", "email": "fernando.lery91@gmail.com", "f_contra": "11-03-2023",
        "anexo1": None, "anexo2": None, "turno": "ART 22", "horario": "ART 22",
        "emerg_nom": "RAUL MONTENEGRO SANHUEZA", "emerg_tel": "942203511", "obs": ""
    },
    {
        "nombre": "GALLEGOS BUSTAMANTE MIGUEL EMILIO", "rut": "007.412.352-8", "cargo": "AYUDANTE DE COCINA",
        "f_nac": "23-01-1981", "nac": "CHILENA", "tel": "942312642", "dir": "PASAJE LOS COPIHUES 212", 
        "est_civil": "S", "email": "jesus.gallegos.bustamante@gmail.com", "f_contra": "01-07-2023",
        "anexo1": "01-07-2023", "anexo2": "02-01-2024", "turno": "5x2", "horario": "15:00 a 1:00",
        "emerg_nom": "MIGUEL ANDRE GALLEGOS", "emerg_tel": "977531122", "obs": ""
    },
    {
        "nombre": "GALLO QUILLO VICTORIO MARCELO", "rut": "022.427.530-0", "cargo": "MAESTRO COCINA",
        "f_nac": "15-05-1996", "nac": "BOLIVIANA", "tel": "311181514", "dir": "CURUTI 2503 VILLA AYQUINA", 
        "est_civil": "S", "email": "marcelogallo@gmail.com", "f_contra": "14-06-2022",
        "anexo1": "14-06-2023", "anexo2": "14-01-2025", "turno": "5x2", "horario": "18:00 a 4:30",
        "emerg_nom": "MARCELA MUÑOZ", "emerg_tel": "996791206", "obs": ""
    },
    {
        "nombre": "GOMEZ PACHON JESUS", "rut": "022.651.789-1", "cargo": "AUXILIAR SERVICIO DE CASINO",
        "f_nac": "24-02-1984", "nac": "COLOMBIANA", "tel": "941544614", "dir": "PEDRO DE VALDIVIA 1675", 
        "est_civil": "S", "email": "jesus.gomezp.@hotmail.com", "f_contra": "21-03-2023",
        "anexo1": None, "anexo2": None, "turno": "7x7", "horario": "10:00 a 22:00",
        "emerg_nom": "VICTOR GOMEZ", "emerg_tel": "941544612", "obs": ""
    },
    {
        "nombre": "GRAN ARAPIZA JUSTINA ROSMET", "rut": "023.647.057-7", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "21-03-1984", "nac": "BOLIVIANA", "tel": "981224558", "dir": "COSTA RICA 2652", 
        "est_civil": "S", "email": "justinagran@gmail.com", "f_contra": "11-04-2024",
        "anexo1": "11-04-2024", "anexo2": "11-05-2024", "turno": "5x2", "horario": "10:00 a 4:30",
        "emerg_nom": "ALBERTO MARTINEZ", "emerg_tel": "971155250", "obs": ""
    },
    {
        "nombre": "GUTIERREZ BARRIA VIRGINIA", "rut": "007.441.808-7", "cargo": "AYUDANTE DE COCINA",
        "f_nac": "18-12-1964", "nac": "CHILENA", "tel": "964213511", "dir": "PASAJE LOS RAMOS 2453", 
        "est_civil": "S", "email": "vickybarria@gmail.com", "f_contra": "21-03-2023",
        "anexo1": "20-05-2024", "anexo2": "20-04-2025", "turno": "5x2", "horario": "10:00 a 4:30",
        "emerg_nom": "ANDRES VALDERRAMA", "emerg_tel": "941443831", "obs": ""
    },
    {
        "nombre": "HINOJOSA CASTRO RUTH ISABEL", "rut": "022.661.385-8", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "29-10-1991", "nac": "BOLIVIANA", "tel": "941121516", "dir": "CALLE LATORRE 137 BARRIO TRANSITORIO", 
        "est_civil": "S", "email": "hinojosalucy@gmail.com", "f_contra": "14-06-2022",
        "anexo1": "14-06-2023", "anexo2": "14-01-2025", "turno": "7x7", "horario": "18:00 a 7:30",
        "emerg_nom": "SANDRA HINOJOSA", "emerg_tel": "966270764", "obs": ""
    },
    {
        "nombre": "LOPEZ DALC, MAURICIO ANTONIO PROPIED", "rut": "016.072.345-k", "cargo": "SUPERVISOR DE CASINO PROPIED",
        "f_nac": "18-03-1985", "nac": "CHILENA", "tel": "942646671", "dir": "PASAJE LATORRE 123 CONCEPCION", 
        "est_civil": "S", "email": "mauricio_salcedo_lopez@yahoo.com", "f_contra": "21-03-2023",
        "anexo1": "22-04-2024", "anexo2": "22-04-2025", "turno": "7x7", "horario": "11:00 a 23:00",
        "emerg_nom": "JAQUELINE LOPEZ", "emerg_tel": "941322250", "obs": ""
    },
    {
        "nombre": "LOPEZ TORRICO ELIZABETH", "rut": "023.272.846-5", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "27-04-1991", "nac": "BOLIVIANA", "tel": "956633365", "dir": "GRAU 1541", 
        "est_civil": "S", "email": "lopeztorricoelizabeth@gmail.com", "f_contra": "14-05-2023",
        "anexo1": "14-05-2023", "anexo2": None, "turno": "7x7", "horario": "13:00 a 1:00",
        "emerg_nom": "MARLENE TABOADA", "emerg_tel": "951177984", "obs": ""
    },
    {
        "nombre": "MAMANI DIAZ DIEGO ALFREDO", "rut": "025.754.015-7", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "19-03-1991", "nac": "BOLIVIANA", "tel": "934255013", "dir": "TOCOPILLA PARCELA 23", 
        "est_civil": "S", "email": "dieguisayala@gmail.com", "f_contra": "21-12-2021",
        "anexo1": "22-11-2023", "anexo2": None, "turno": "7x7", "horario": "10:00 a 22:00",
        "emerg_nom": "MIGUEL TABOADA", "emerg_tel": "965903250", "obs": ""
    },
    {
        "nombre": "MAMANI VILLALOBOS LAURA GRICEL", "rut": "022.427.530-0", "cargo": "AUXILIAR DE CASINO",
        "f_nac": "05-05-2002", "nac": "BOLIVIANA", "tel": "936411171", "dir": "VILLALOBOS 2572", 
        "est_civil": "S", "email": "gricelm@gmail.com", "f_contra": "01-08-2023",
        "anexo1": "01-08-2022", "anexo2": None, "turno": "ART 22", "horario": "18:00 a 7:30",
        "emerg_nom": "CRISTINA VILLALOBOS", "emerg_tel": "941612735", "obs": ""
    },
    {
        "nombre": "MAMANI VIRGO RONAL", "rut": "025.475.815-5", "cargo": "PANADERO",
        "f_nac": "21-11-2000", "nac": "BOLIVIANA", "tel": "986975123", "dir": "CARLOS CISTERNA 2473", 
        "est_civil": "S", "email": "ronalyvirgo@gmail.com", "f_contra": "01-03-2024",
        "anexo1": "01-03-2024", "anexo2": None, "turno": "7x7", "horario": "6:00 a 18:30",
        "emerg_nom": "ADRIAN QUISPE", "emerg_tel": "", "obs": ""
    },
    {
        "nombre": "MARTINEZ MARIA", "rut": "026.197.431-1", "cargo": "AYUDANTE DE COCINA",
        "f_nac": "01-08-1977", "nac": "DOMINICANA", "tel": "981245782", "dir": "", 
        "est_civil": "S", "email": "maria021980@gmail.com", "f_contra": "01-06-2022",
        "anexo1": None, "anexo2": None, "turno": "7x7", "horario": "7:00 a 19:30",
        "emerg_nom": "KENNY ANTONIO GARCIA", "emerg_tel": "942646112", "obs": ""
    },
]

def import_data():
    for data in employee_data:
        # Split names (Assuming first word is first name, rest are last names for simplicity in this script)
        # However, the image shows "LAST NAME1 LAST NAME2, FIRST NAME" or similar.
        # Let's clean RUT first to find existing
        clean_rut = data["rut"].replace(".", "")
        
        # Name split: image shows "AGUIRRE CRUZ FRANCISCA" -> Lname1 Lname2 Fname
        parts = data["nombre"].split()
        if len(parts) >= 3:
            apellido = f"{parts[0]} {parts[1]}"
            nombre = " ".join(parts[2:])
        else:
            apellido = parts[0]
            nombre = " ".join(parts[1:]) if len(parts) > 1 else ""

        defaults = {
            "nombre": nombre,
            "apellido": apellido,
            "cargo": data["cargo"],
            "fecha_nacimiento": parse_date(data["f_nac"]),
            "nacionalidad": data["nac"],
            "telefono": data["tel"],
            "direccion": data["dir"],
            "estado_civil": data["est_civil"],
            "email": data["email"],
            "fecha_contrato": parse_date(data["f_contra"]),
            "anexo_1": parse_date(data["anexo1"]),
            "anexo_2": parse_date(data["anexo2"]),
            "turno": data["turno"],
            "horario": data["horario"],
            "emergencia_nombre": data["emerg_nom"],
            "emergencia_telefono": data["emerg_tel"],
            "observaciones": data["obs"],
            "area": "OTRO",
            "estado": "ACTIVO",
        }

        obj, created = Empleado.objects.update_or_create(
            rut=clean_rut,
            defaults=defaults
        )
        status = "Created" if created else "Updated"
        print(f"{status}: {obj.nombre} {obj.apellido} ({obj.rut})")

if __name__ == "__main__":
    import_data()
