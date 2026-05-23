from __future__ import annotations

from datetime import date, timedelta

from configuracion.ajustes import ARCHIVO_DATOS
from controlador.ControlOferta import ControlOferta
from controlador.ControlUsuario import ControlUsuario
from modelo.Usuario import Usuario
from utilidades.ManejoDatos import ManejoDatos


def inicializar_archivos_dat() -> None:
    for ruta in ARCHIVO_DATOS.values():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if not ruta.exists():
            ruta.touch()


def sembrar_datos_prueba() -> None:
    inicializar_archivos_dat()
    if Usuario.cargar_todos():
        return

    usuarios = ControlUsuario()
    ofertas = ControlOferta()

    usuarios.registrar_administrador("Admin General", "admin@uleam.edu.ec", "admin123")
    usuarios.registrar_coordinador("Coord Practicas", "coord@uleam.edu.ec", "coord123")
    usuarios.registrar_tutor_academico(
        "Tutor Academico",
        "tutor.academico@uleam.edu.ec",
        "tutor123",
        "Software",
    )
    usuarios.registrar_estudiante(
        "Ana Estudiante",
        "ana@uleam.edu.ec",
        "ana123",
        "1310000001",
        "Software",
        7,
        True,
    )

    empresa = ofertas.registrar_empresa(
        "Tech Andina",
        "contacto@techandina.com",
        "Tech Andina S.A.",
        "1399999999001",
        "Tecnologia",
        "Manta",
        "Crear soluciones digitales utiles.",
        "Ser referente regional en innovacion.",
        True,
    )
    usuarios.registrar_tutor_empresarial(
        "Tutor Empresarial",
        "tutor.empresarial@techandina.com",
        "tutor123",
        empresa.id_empresa,
        "Lider tecnico",
    )
    ofertas.crear_oferta(
        empresa.id_empresa,
        "Practicante de desarrollo Python",
        "Apoyo en desarrollo de sistemas internos.",
        "Python basico, Git y buenas practicas.",
        "Desarrollo de software",
        3,
        date.today() + timedelta(days=30),
    )
    for nombre in [
        "postulaciones",
        "practicas",
        "actividades",
        "formularios",
        "documentos",
        "solicitudes",
        "convenios",
        "notificaciones",
    ]:
        ManejoDatos(nombre).guardar({})
