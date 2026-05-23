"""Menu principal de la aplicacion."""

from __future__ import annotations

from configuracion.ajustes import ROLES
from controlador.ControlUsuario import ControlUsuario
from modelo.Usuario import (
    Administrador,
    Coordinador,
    Estudiante,
    TutorAcademico,
    TutorEmpresarial,
)
from utilidades.Excepciones import SistemaPracticasError
from vista.VistaAdministrador import VistaAdministrador
from vista.VistaCoordinador import VistaCoordinador
from vista.VistaEstudiante import VistaEstudiante
from vista.VistaTutorAcademico import VistaTutorAcademico
from vista.VistaTutorEmpresarial import VistaTutorEmpresarial
from vista.ValidacionDatos import leer_texto, pausar


class MainMenu:
    def __init__(self) -> None:
        self.usuarios = ControlUsuario()

    def iniciar(self) -> None:
        while True:
            print("\n=== Sistema de Gestion de Practicas Preprofesionales ===")
            print("1. Iniciar sesion")
            print("0. Salir")
            opcion = leer_texto("Seleccione: ")

            if opcion == "1":
                self._login()
            elif opcion == "0":
                print("Hasta luego.")
                return

    def _login(self) -> None:
        try:
            usuario = self.usuarios.login(
                leer_texto("Email: "),
                leer_texto("Password: "),
            )
            if isinstance(usuario, Administrador) or usuario.rol == ROLES["ADMINISTRADOR"]:
                VistaAdministrador(usuario).mostrar()
            elif isinstance(usuario, Coordinador) or usuario.rol == ROLES["COORDINADOR"]:
                VistaCoordinador(usuario).mostrar()
            elif isinstance(usuario, Estudiante) or usuario.rol == ROLES["ESTUDIANTE"]:
                VistaEstudiante(usuario).mostrar()
            elif (
                isinstance(usuario, TutorAcademico)
                or usuario.rol == ROLES["TUTOR_ACADEMICO"]
            ):
                VistaTutorAcademico(usuario).mostrar()
            elif (
                isinstance(usuario, TutorEmpresarial)
                or usuario.rol == ROLES["TUTOR_EMPRESARIAL"]
            ):
                VistaTutorEmpresarial(usuario).mostrar()
            else:
                print("Rol sin vista de consola asignada.")
                pausar()
        except SistemaPracticasError as error:
            print(f"Error: {error}")
            pausar()
