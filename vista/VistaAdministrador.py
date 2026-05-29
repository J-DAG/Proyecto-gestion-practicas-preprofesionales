"""Vista de consola para administradores."""

from __future__ import annotations

from controlador.ControlAdministrador import ControlAdministrador
from controlador.ControlOferta import ControlOferta
from controlador.ControlUsuario import ControlUsuario
from modelo.Usuario import Administrador
from utilidades.Excepciones import SistemaPracticasError
from vista.ValidacionDatos import imprimir_tabla, leer_bool, leer_entero, leer_texto, pausar


class VistaAdministrador:
    def __init__(self, usuario: Administrador) -> None:
        self.usuario = usuario
        self.admin = ControlAdministrador()
        self.ofertas = ControlOferta()
        self.usuarios = ControlUsuario()

    def mostrar(self) -> None:
        while True:
            print("\n=== Panel Administrador ===")
            print("1. Registrar estudiante")
            print("2. Registrar coordinador")
            print("3. Registrar administrador")
            print("4. Registrar tutor academico")
            print("5. Registrar tutor empresarial")
            print("6. Listar usuarios")
            print("7. Activar/desactivar usuario")
            print("8. Reportes")
            print("9. Mantenimiento general")
            print("0. Cerrar sesion")
            opcion = leer_texto("Seleccione: ")

            acciones = {
                "1": self._registrar_estudiante,
                "2": self._registrar_coordinador,
                "3": self._registrar_administrador,
                "4": self._registrar_tutor_academico,
                "5": self._registrar_tutor_empresarial,
                "6": self._listar_usuarios,
                "7": self._activar_desactivar,
                "8": self._reportes,
                "9": self._mantenimiento,
            }
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                accion()

    def _registrar_estudiante(self) -> None:
        try:
            estudiante = self.usuarios.registrar_estudiante(
                leer_texto("Nombres: "),
                leer_texto("Apellidos: "),
                leer_texto("Email: "),
                leer_texto("Password: "),
                leer_texto("Cedula: "),
                leer_texto("Carrera: "),
                leer_entero("Ciclo actual: "),
                leer_bool("Matriculado"),
            )
            print(f"Estudiante registrado: {estudiante.id_usuario}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _registrar_coordinador(self) -> None:
        try:
            coordinador = self.usuarios.registrar_coordinador(
                leer_texto("Nombres: "),
                leer_texto("Apellidos: "),
                leer_texto("Email: "),
                leer_texto("Password: "),
            )
            print(f"Coordinador registrado: {coordinador.id_usuario}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _registrar_administrador(self) -> None:
        try:
            administrador = self.usuarios.registrar_administrador(
                leer_texto("Nombres: "),
                leer_texto("Apellidos: "),
                leer_texto("Email: "),
                leer_texto("Password: "),
            )
            print(f"Administrador registrado: {administrador.id_usuario}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _registrar_tutor_academico(self) -> None:
        try:
            tutor = self.usuarios.registrar_tutor_academico(
                leer_texto("Nombres: "),
                leer_texto("Apellidos: "),
                leer_texto("Email: "),
                leer_texto("Password: "),
                leer_texto("Carrera: "),
            )
            print(f"Tutor academico registrado: {tutor.id_usuario}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _registrar_tutor_empresarial(self) -> None:
        try:
            self._mostrar_empresas()
            tutor = self.usuarios.registrar_tutor_empresarial(
                leer_texto("Nombres: "),
                leer_texto("Apellidos: "),
                leer_texto("Email: "),
                leer_texto("Password: "),
                leer_texto("ID empresa: "),
                leer_texto("Cargo: "),
            )
            print(f"Tutor empresarial registrado: {tutor.id_usuario}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _listar_usuarios(self) -> None:
        imprimir_tabla(self.usuarios.listar_usuarios())
        pausar()

    def _activar_desactivar(self) -> None:
        try:
            self._mostrar_usuarios()
            usuario = self.admin.activar_desactivar_cuenta(
                leer_texto("ID usuario: "),
                leer_bool("Activo"),
            )
            print(f"Usuario actualizado: {usuario.id_usuario} activo={usuario.activo}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _reportes(self) -> None:
        for nombre, total in self.admin.generar_reportes().items():
            print(f"{nombre}: {total}")
        pausar()

    def _mantenimiento(self) -> None:
        for nombre, total in self.admin.mantenimiento_general().items():
            print(f"{nombre}.dat: {total} registros")
        pausar()

    def _mostrar_empresas(self) -> None:
        empresas = self.ofertas.listar_empresas()
        print("\nEmpresas registradas:")
        if not empresas:
            print("No hay empresas registradas.")
        for empresa in empresas:
            print(f"- {empresa.id_empresa} | {empresa.nombre_empresa} | RUC: {empresa.ruc}")

    def _mostrar_usuarios(self) -> None:
        usuarios = self.usuarios.listar_usuarios()
        print("\nUsuarios registrados:")
        if not usuarios:
            print("No hay usuarios registrados.")
        for usuario in usuarios:
            estado = "activo" if usuario.activo else "inactivo"
            print(
                f"- {usuario.id_usuario} | {usuario.nombre} | "
                f"{usuario.email} | {usuario.rol} | {estado}"
            )
