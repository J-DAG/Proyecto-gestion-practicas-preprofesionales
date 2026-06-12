
from __future__ import annotations

from typing import Optional

from configuracion.ajustes import ROLES
from modelo.Empresa import Empresa
from modelo.Usuario import (
    Administrador,
    Coordinador,
    Estudiante,
    TutorAcademico,
    TutorEmpresarial,
    Usuario,
)
from utilidades.Excepciones import AutenticacionError, EntidadDuplicadaError, ValidacionError
from utilidades.IDgenerator import generar_id
from utilidades.ManejoDatos import ManejoDatos
from utilidades.ValidacionCedula import validar_cedula_ecuatoriana

class ControlUsuario:
    def registrar_estudiante(
            self,
            nombres: str,
            apellidos: str,
            cedula: str,
            email: str,
            password: str,
            carrera: str,
            ciclo_actual: int,
            matriculado: bool,
    ) -> Estudiante:
        cedula = self._validar_datos_unicos(email, cedula)
        estudiante = Estudiante(
            id_usuario=generar_id("EST"),
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            email=email,
            password=password,
            rol=ROLES["ESTUDIANTE"],
            carrera=carrera,
            ciclo_actual=ciclo_actual,
            matriculado=matriculado,
        )
        estudiante.guardar()
        return estudiante

    def registrar_coordinador(
            self,
            nombres: str,
            apellidos: str,
            cedula: str,
            email: str,
            password: str,
    ) -> Coordinador:
        cedula = self._validar_datos_unicos(email, cedula)
        coordinador = Coordinador(
            id_usuario=generar_id("COO"),
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            email=email,
            password=password,
            rol=ROLES["COORDINADOR"],
        )
        coordinador.guardar()
        return coordinador

    def registrar_tutor_academico(
            self,
            nombres: str,
            apellidos: str,
            cedula: str,
            email: str,
            password: str,
            carrera: str,
    ) -> TutorAcademico:
        cedula = self._validar_datos_unicos(email, cedula)
        tutor = TutorAcademico(
            id_usuario=generar_id("TAC"),
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            email=email,
            password=password,
            rol=ROLES["TUTOR_ACADEMICO"],
            carrera=carrera,
        )
        tutor.guardar()
        return tutor

    def registrar_tutor_empresarial(
            self,
            nombres: str,
            apellidos: str,
            cedula: str,
            email: str,
            password: str,
            id_empresa: str,
            cargo: str,
    ) -> TutorEmpresarial:
        cedula = self._validar_datos_unicos(email, cedula)
        Empresa.obtener_por_id(id_empresa)
        tutor = TutorEmpresarial(
            id_usuario=generar_id("TEM"),
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            email=email,
            password=password,
            rol=ROLES["TUTOR_EMPRESARIAL"],
            id_empresa=id_empresa,
            cargo=cargo,
        )
        tutor.guardar()
        return tutor

    def registrar_administrador(
            self,
            nombres: str,
            apellidos: str,
            cedula: str,
            email: str,
            password: str,
    ) -> Administrador:
        cedula = self._validar_datos_unicos(email, cedula)
        administrador = Administrador(
            id_usuario=generar_id("ADM"),
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            email=email,
            password=password,
            rol=ROLES["ADMINISTRADOR"],
        )
        administrador.guardar()
        return administrador

    def login(self, email: str, password: str) -> Usuario:
        usuario = ManejoDatos("usuarios").buscar_por_campo("email", email)
        if usuario is None:
            usuario = Usuario.buscar_por_id(email)
        if usuario is None or not usuario.autenticar(password):
            raise AutenticacionError("Credenciales invalidas.")
        return usuario

    def actualizar_usuario(self, usuario: Usuario) -> None:
        usuario.guardar()

    def listar_usuarios(self) -> list[Usuario]:
        return Usuario.cargar_todos()

    def buscar_usuario(self, id_usuario: str) -> Optional[Usuario]:
        return Usuario.buscar_por_id(id_usuario)

    def activar_desactivar_usuario(self, id_usuario: str, activo: bool) -> Usuario:
        usuario = Usuario.obtener_por_id(id_usuario)
        usuario.activo = activo
        usuario.guardar()
        return usuario

    def _validar_datos_unicos(self, email: str, cedula: str) -> str:
        if "@" not in email:
            raise ValidacionError("El email ingresado no tiene un formato valido.")
        try:
            cedula = validar_cedula_ecuatoriana(cedula)
        except ValueError as error:
            raise ValidacionError(str(error)) from error
        if ManejoDatos("usuarios").buscar_por_campo("email", email):
            raise EntidadDuplicadaError(f"Ya existe un usuario con email {email}.")
        if ManejoDatos("usuarios").buscar_por_campo("cedula", cedula):
            raise EntidadDuplicadaError(f"Ya existe un usuario con cedula {cedula}.")
        return cedula
