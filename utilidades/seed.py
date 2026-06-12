from __future__ import annotations

from configuracion.ajustes import ARCHIVO_DATOS, ROLES
from modelo.Usuario import Administrador, Usuario
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

    administrador = Administrador(
        id_usuario="admin",
        nombres="Administrador",
        apellidos="General",
        cedula="1300000005",
        email="admin@local",
        password="admin",
        rol=ROLES["ADMINISTRADOR"],
    )
    administrador.guardar()

    for nombre in ARCHIVO_DATOS:
        if nombre == "usuarios":
            continue
        ManejoDatos(nombre).guardar({})
