from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATOS_DIR = BASE_DIR / "datos"

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
}

ROLES = {
    "ADMINISTRADOR": "administrador",
    "COORDINADOR": "coordinador",
    "ESTUDIANTE": "estudiante",
    "TUTOR_ACADEMICO": "tutor_academico",
    "TUTOR_EMPRESARIAL": "tutor_empresarial",
}