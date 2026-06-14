from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATOS_DIR = BASE_DIR / "datos"
HORAS_MAXIMAS_PRACTICA = 240


ARCHIVO_DATOS = {
    "usuarios": DATOS_DIR / "usuarios.dat",
    "empresas": DATOS_DIR / "empresas.dat",
    "ofertas": DATOS_DIR / "ofertas.dat",
    "postulaciones": DATOS_DIR / "postulaciones.dat",
    "practicas": DATOS_DIR / "practicas.dat",
    "actividades": DATOS_DIR / "actividades.dat",
    "formularios": DATOS_DIR / "formularios.dat",
    "documentos": DATOS_DIR / "documentos.dat",
    "solicitudes": DATOS_DIR / "solicitudes.dat",
    "convenios": DATOS_DIR / "convenios.dat",
    "notificaciones": DATOS_DIR / "notificaciones.dat",
}

ROLES = {
    "ADMINISTRADOR": "administrador",
    "COORDINADOR": "coordinador",
    "ESTUDIANTE": "estudiante",
    "TUTOR_ACADEMICO": "tutor_academico",
    "TUTOR_EMPRESARIAL": "tutor_empresarial",
}
