from __future__ import annotations

from configuracion.ajustes import ROLES
from controlador.ControlNotificacion import ControlNotificacion
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Practica import Actividad, Practica
from modelo.Usuario import Usuario
from utilidades.Excepciones import ReglaNegocioError, ValidacionError
from utilidades.ManejoDatos import ManejoDatos


class ControlAdministrador:
    def listar_entidades(self, nombre_archivo: str) -> list[object]:
        return ManejoDatos(nombre_archivo).cargar()

    def activar_desactivar_cuenta(
        self,
        id_usuario: str,
        activo: bool,
        id_reemplazo: str | None = None,
    ) -> Usuario:
        usuario = Usuario.obtener_por_id(id_usuario)
        if not activo:
            self._validar_desactivacion(usuario, id_reemplazo)
        usuario.activo = activo
        usuario.guardar()
        return usuario

    def listar_practicas_activas_asignadas(self, id_usuario: str) -> list[Practica]:
        usuario = Usuario.obtener_por_id(id_usuario)
        if usuario.rol == ROLES["TUTOR_ACADEMICO"]:
            return [
                practica
                for practica in Practica.cargar_todos()
                if practica.estado == "activa" and practica.id_tutor_academico == id_usuario
            ]
        if usuario.rol == ROLES["TUTOR_EMPRESARIAL"]:
            return [
                practica
                for practica in Practica.cargar_todos()
                if practica.estado == "activa" and practica.tutor_empresarial == id_usuario
            ]
        return []

    def _validar_desactivacion(
        self,
        usuario: Usuario,
        id_reemplazo: str | None,
    ) -> None:
        if usuario.rol == ROLES["COORDINADOR"]:
            self._validar_coordinador_activo_restante(usuario.id_usuario)
            return

        if usuario.rol == ROLES["ESTUDIANTE"]:
            self._validar_desactivacion_estudiante(usuario)
            return

        if usuario.rol not in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            return

        practicas = self.listar_practicas_activas_asignadas(usuario.id_usuario)
        if not practicas:
            return

        if not id_reemplazo:
            raise ValidacionError(
                "Debe indicar un tutor reemplazo antes de desactivar este tutor."
            )

        reemplazo = Usuario.obtener_por_id(id_reemplazo)
        if reemplazo.rol != usuario.rol:
            raise ReglaNegocioError("El reemplazo debe tener el mismo rol del tutor desactivado.")
        if not reemplazo.activo:
            raise ReglaNegocioError("El tutor reemplazo debe estar activo.")
        if reemplazo.id_usuario == usuario.id_usuario:
            raise ReglaNegocioError("El tutor reemplazo debe ser diferente al tutor desactivado.")

        self._reasignar_practicas_tutor(usuario, reemplazo, practicas)

    def _validar_coordinador_activo_restante(self, id_usuario: str) -> None:
        coordinadores_activos = [
            usuario
            for usuario in Usuario.cargar_todos()
            if usuario.rol == ROLES["COORDINADOR"]
            and usuario.activo
            and usuario.id_usuario != id_usuario
        ]
        if not coordinadores_activos:
            raise ReglaNegocioError("No se puede desactivar el ultimo coordinador activo.")

    def _validar_desactivacion_estudiante(self, estudiante: Usuario) -> None:
        practica_activa = [
            practica
            for practica in Practica.cargar_todos()
            if practica.id_estudiante == estudiante.id_usuario
            and practica.estado == "activa"
        ]
        if practica_activa:
            raise ReglaNegocioError(
                "No se puede desactivar un estudiante con practica activa. "
                "Primero debe finalizarse la practica."
            )

        self._rechazar_postulaciones_abiertas_estudiante(estudiante)

    def _rechazar_postulaciones_abiertas_estudiante(self, estudiante: Usuario) -> None:
        estados_abiertos = {"pendiente", "validada", "en_terna"}
        postulaciones = [
            postulacion
            for postulacion in Postulacion.cargar_todos()
            if postulacion.id_estudiante == estudiante.id_usuario
            and postulacion.estado in estados_abiertos
        ]

        for postulacion in postulaciones:
            postulacion.rechazar()
            postulacion.guardar()

        if postulaciones:
            ControlNotificacion().crear_notificacion(
                estudiante.id_usuario,
                "Postulaciones cerradas",
                (
                    "Sus postulaciones abiertas fueron rechazadas automaticamente "
                    "por desactivacion de la cuenta."
                ),
                "postulacion",
            )

    def _reasignar_practicas_tutor(
        self,
        tutor_anterior: Usuario,
        tutor_reemplazo: Usuario,
        practicas: list[Practica],
    ) -> None:
        for practica in practicas:
            if tutor_anterior.rol == ROLES["TUTOR_ACADEMICO"]:
                practica.id_tutor_academico = tutor_reemplazo.id_usuario
            elif tutor_anterior.rol == ROLES["TUTOR_EMPRESARIAL"]:
                practica.tutor_empresarial = tutor_reemplazo.id_usuario
            practica.guardar()
            self._notificar_reasignacion(practica, tutor_anterior, tutor_reemplazo)

    def _notificar_reasignacion(
        self,
        practica: Practica,
        tutor_anterior: Usuario,
        tutor_reemplazo: Usuario,
    ) -> None:
        notificaciones = ControlNotificacion()
        mensaje = (
            f"La practica {practica.id_practica} fue reasignada de "
            f"{tutor_anterior.nombre} a {tutor_reemplazo.nombre}."
        )
        notificaciones.crear_notificacion(
            tutor_reemplazo.id_usuario,
            "Practica reasignada",
            mensaje,
            "practica",
        )
        notificaciones.crear_notificacion(
            practica.id_estudiante,
            "Cambio de tutor",
            mensaje,
            "practica",
        )

    def generar_reportes(self) -> dict[str, int]:
        practicas = Practica.cargar_todos()
        return {
            "usuarios": len(Usuario.cargar_todos()),
            "empresas": len(Empresa.cargar_todos()),
            "ofertas": len(Oferta.cargar_todos()),
            "postulaciones": len(Postulacion.cargar_todos()),
            "practicas_activas": len([p for p in practicas if p.estado == "activa"]),
            "practicas_finalizadas": len([p for p in practicas if p.estado == "finalizada"]),
            "actividades": len(Actividad.cargar_todos()),
        }

    def mantenimiento_general(self) -> dict[str, int]:
        archivos = [
            "usuarios",
            "empresas",
            "ofertas",
            "postulaciones",
            "practicas",
            "actividades",
            "formularios",
            "documentos",
            "solicitudes",
            "convenios",
        ]
        return {archivo: len(ManejoDatos(archivo).cargar()) for archivo in archivos}
