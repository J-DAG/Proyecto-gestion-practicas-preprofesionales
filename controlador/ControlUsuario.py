
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

class ControlUsuario:
    def registrar_estudiante(
            self,
            nombres: str,
            apellidos: str,
            email: str,
            password: str,
            cedula: str,
            carrera: str,
            ciclo_actual: int,
            matriculado: bool,
    ) -> Estudiante:
        self._validar_email_unico(email)
        estudiante = Estudiante(
            id_usuario=generar_id("EST"),
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            password=password,
            rol=ROLES["ESTUDIANTE"],
            cedula=cedula,
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
            email: str,
            password: str,
    ) -> Coordinador:
        self._validar_email_unico(email)
        coordinador = Coordinador(
            id_usuario=generar_id("COO"),
            nombres=nombres,
            apellidos=apellidos,
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
            email: str,
            password: str,
            carrera: str,
    ) -> TutorAcademico:
        self._validar_email_unico(email)
        tutor = TutorAcademico(
            id_usuario=generar_id("TAC"),
            nombres=nombres,
            apellidos=apellidos,
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
            email: str,
            password: str,
            id_empresa: str,
            cargo: str,
    ) -> TutorEmpresarial:
        self._validar_email_unico(email)
        Empresa.obtener_por_id(id_empresa)
        tutor = TutorEmpresarial(
            id_usuario=generar_id("TEM"),
            nombres=nombres,
            apellidos=apellidos,
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
            email: str,
            password: str,
    ) -> Administrador:
        self._validar_email_unico(email)
        administrador = Administrador(
            id_usuario=generar_id("ADM"),
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            password=password,
            rol=ROLES["ADMINISTRADOR"],
        )
        administrador.guardar()
        return administrador

    def login(self, email: str, password: str) -> Usuario:
        usuario = ManejoDatos("usuarios").buscar_por_campo("email", email)
        if usuario is None or not usuario.autenticar(password):
            raise AutenticacionError("Credenciales invalidas o cuenta inactiva.")
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

    def _validar_email_unico(self, email: str) -> None:
        if "@" not in email:
            raise ValidacionError("El email ingresado no tiene un formato valido.")
        if ManejoDatos("usuarios").buscar_por_campo("email", email):
            raise EntidadDuplicadaError(f"Ya existe un usuario con email {email}.")
