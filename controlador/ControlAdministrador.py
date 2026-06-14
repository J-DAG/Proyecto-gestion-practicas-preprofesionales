from __future__ import annotations

from datetime import date
from pathlib import Path

from modelo.configuracion.ajustes import DATOS_DIR, ROLES
from controlador.ControlNotificacion import ControlNotificacion
from modelo.Documentos import Documento, Formulario, SolicitudAutorizacion
from modelo.Empresa import Empresa
from modelo.Notificacion import Notificacion
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Practica import Actividad, Practica
from modelo.Usuario import Usuario
from modelo.utilidades.Excepciones import ReglaNegocioError, ValidacionError
from modelo.utilidades.ManejoDatos import ManejoDatos


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

    def eliminar_usuario(self, id_usuario: str, id_reemplazo: str | None = None) -> None:
        usuario = Usuario.obtener_por_id(id_usuario)
        self._validar_eliminacion_fisica(usuario, id_reemplazo)
        if usuario.rol == ROLES["ESTUDIANTE"]:
            self._eliminar_dependencias_estudiante(usuario)
        if usuario.rol in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            self._reasignar_referencias_tutor_para_eliminar(usuario, id_reemplazo)

        usuarios = {
            usuario_guardado.id_usuario: usuario_guardado
            for usuario_guardado in Usuario.cargar_todos()
            if usuario_guardado.id_usuario != usuario.id_usuario
        }
        ManejoDatos("usuarios").guardar(usuarios, "id_usuario")
        self._eliminar_notificaciones_usuario(usuario.id_usuario)

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

    def tutor_requiere_reemplazo_para_eliminar(self, id_usuario: str) -> bool:
        usuario = Usuario.obtener_por_id(id_usuario)
        if usuario.rol not in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            return False
        return bool(self._motivos_bloqueo_eliminacion_tutor(usuario))

    def _validar_eliminacion_fisica(
        self,
        usuario: Usuario,
        id_reemplazo: str | None = None,
    ) -> None:
        if usuario.rol == ROLES["COORDINADOR"]:
            self._validar_coordinador_activo_restante(usuario.id_usuario)
        if usuario.rol == ROLES["ADMINISTRADOR"]:
            self._validar_administrador_activo_restante(usuario.id_usuario)

        if usuario.rol in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            self._validar_reemplazo_eliminacion_tutor(usuario, id_reemplazo)
            return

        motivos = self._motivos_bloqueo_eliminacion(usuario)
        if motivos:
            detalle = "; ".join(motivos)
            raise ReglaNegocioError(
                "No se puede eliminar fisicamente este usuario porque "
                f"{detalle}. Use la desactivacion si solo necesita impedir el acceso."
            )

    def _validar_administrador_activo_restante(self, id_usuario: str) -> None:
        administradores_activos = [
            usuario
            for usuario in Usuario.cargar_todos()
            if usuario.rol == ROLES["ADMINISTRADOR"]
            and usuario.activo
            and usuario.id_usuario != id_usuario
        ]
        if not administradores_activos:
            raise ReglaNegocioError("No se puede eliminar el ultimo administrador activo.")

    def _motivos_bloqueo_eliminacion(self, usuario: Usuario) -> list[str]:
        motivos: list[str] = []

        if usuario.rol in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            motivos.extend(self._motivos_bloqueo_eliminacion_tutor(usuario))

        return motivos

    def _motivos_bloqueo_eliminacion_tutor(self, usuario: Usuario) -> list[str]:
        motivos: list[str] = []

        if usuario.rol == ROLES["TUTOR_ACADEMICO"]:
            if any(p.id_tutor_academico == usuario.id_usuario for p in Practica.cargar_todos()):
                motivos.append("esta asignado como tutor academico en practicas")
            if any(
                a.id_tutor_academico_aprobador == usuario.id_usuario
                for a in Actividad.cargar_todos()
            ):
                motivos.append("tiene actividades aprobadas registradas")

        if usuario.rol == ROLES["TUTOR_EMPRESARIAL"]:
            if any(p.tutor_empresarial == usuario.id_usuario for p in Practica.cargar_todos()):
                motivos.append("esta asignado como tutor empresarial en practicas")
            if any(
                a.tutor_empresarial_completador == usuario.id_usuario
                for a in Actividad.cargar_todos()
            ):
                motivos.append("tiene actividades completadas registradas")

        return motivos

    def _validar_reemplazo_eliminacion_tutor(
        self,
        tutor: Usuario,
        id_reemplazo: str | None,
    ) -> None:
        motivos = self._motivos_bloqueo_eliminacion_tutor(tutor)
        if not motivos:
            return

        if not id_reemplazo:
            raise ValidacionError(
                "Debe indicar un tutor reemplazo antes de eliminar este tutor."
            )

        reemplazo = Usuario.obtener_por_id(id_reemplazo)
        if reemplazo.rol != tutor.rol:
            raise ReglaNegocioError("El reemplazo debe tener el mismo rol del tutor eliminado.")
        if not reemplazo.activo:
            raise ReglaNegocioError("El tutor reemplazo debe estar activo.")
        if reemplazo.id_usuario == tutor.id_usuario:
            raise ReglaNegocioError("El tutor reemplazo debe ser diferente al tutor eliminado.")

    def _reasignar_referencias_tutor_para_eliminar(
        self,
        tutor: Usuario,
        id_reemplazo: str | None,
    ) -> None:
        if not id_reemplazo:
            return

        reemplazo = Usuario.obtener_por_id(id_reemplazo)
        practicas_reasignadas = self._reasignar_practicas_tutor_eliminado(tutor, reemplazo)
        self._reasignar_actividades_tutor_eliminado(tutor, reemplazo)

        for practica in practicas_reasignadas:
            if practica.estado == "activa":
                self._notificar_reasignacion(practica, tutor, reemplazo)

    def _reasignar_practicas_tutor_eliminado(
        self,
        tutor: Usuario,
        reemplazo: Usuario,
    ) -> list[Practica]:
        practicas_reasignadas: list[Practica] = []
        for practica in Practica.cargar_todos():
            reasignada = False
            if tutor.rol == ROLES["TUTOR_ACADEMICO"] and practica.id_tutor_academico == tutor.id_usuario:
                practica.id_tutor_academico = reemplazo.id_usuario
                reasignada = True
            if tutor.rol == ROLES["TUTOR_EMPRESARIAL"] and practica.tutor_empresarial == tutor.id_usuario:
                practica.tutor_empresarial = reemplazo.id_usuario
                reasignada = True
            if reasignada:
                practica.guardar()
                practicas_reasignadas.append(practica)
        return practicas_reasignadas

    def _reasignar_actividades_tutor_eliminado(
        self,
        tutor: Usuario,
        reemplazo: Usuario,
    ) -> None:
        for actividad in Actividad.cargar_todos():
            reasignada = False
            if (
                tutor.rol == ROLES["TUTOR_ACADEMICO"]
                and actividad.id_tutor_academico_aprobador == tutor.id_usuario
            ):
                actividad.id_tutor_academico_aprobador = reemplazo.id_usuario
                reasignada = True
            if (
                tutor.rol == ROLES["TUTOR_EMPRESARIAL"]
                and actividad.tutor_empresarial_completador == tutor.id_usuario
            ):
                actividad.tutor_empresarial_completador = reemplazo.id_usuario
                reasignada = True
            if reasignada:
                actividad.guardar()

    def _eliminar_dependencias_estudiante(self, estudiante: Usuario) -> None:
        postulaciones_estudiante = [
            postulacion
            for postulacion in Postulacion.cargar_todos()
            if postulacion.id_estudiante == estudiante.id_usuario
        ]
        ids_postulaciones = {
            postulacion.id_postulacion
            for postulacion in postulaciones_estudiante
        }
        practicas_estudiante = [
            practica
            for practica in Practica.cargar_todos()
            if practica.id_estudiante == estudiante.id_usuario
            or practica.id_postulacion in ids_postulaciones
        ]
        ids_practicas = {
            practica.id_practica
            for practica in practicas_estudiante
        }

        self._restaurar_cupos_postulaciones_aceptadas(postulaciones_estudiante)
        self._eliminar_archivos_malla_postulaciones(postulaciones_estudiante)
        self._eliminar_registros_por_practica(ids_practicas)
        self._eliminar_registros_estudiante(estudiante.id_usuario)

    def _restaurar_cupos_postulaciones_aceptadas(self, postulaciones: list[Postulacion]) -> None:
        for postulacion in postulaciones:
            if postulacion.estado != "aceptada":
                continue
            oferta = Oferta.buscar_por_id(postulacion.id_oferta)
            if oferta is None:
                continue
            oferta.cupos += 1
            if oferta.estado == "cerrada" and oferta.fecha_cierre >= date.today():
                oferta.estado = "abierta"
            oferta.guardar()

    def _eliminar_archivos_malla_postulaciones(self, postulaciones: list[Postulacion]) -> None:
        directorio_documentos = (DATOS_DIR / "documentos_postulacion").resolve()
        for postulacion in postulaciones:
            if not postulacion.ruta_documento_malla:
                continue
            ruta = Path(postulacion.ruta_documento_malla)
            try:
                ruta_resuelta = ruta.resolve()
                if ruta.exists() and ruta.is_file() and directorio_documentos in ruta_resuelta.parents:
                    ruta.unlink()
            except OSError:
                continue

    def _eliminar_registros_por_practica(self, ids_practicas: set[str]) -> None:
        if not ids_practicas:
            return

        actividades = {
            actividad.id_actividad: actividad
            for actividad in Actividad.cargar_todos()
            if actividad.id_practica not in ids_practicas
        }
        formularios = {
            formulario.id_formulario: formulario
            for formulario in Formulario.cargar_todos()
            if formulario.id_practica not in ids_practicas
        }
        documentos = {
            documento.id_documento: documento
            for documento in Documento.cargar_todos()
            if documento.id_practica not in ids_practicas
        }
        practicas = {
            practica.id_practica: practica
            for practica in Practica.cargar_todos()
            if practica.id_practica not in ids_practicas
        }

        ManejoDatos("actividades").guardar(actividades, "id_actividad")
        ManejoDatos("formularios").guardar(formularios, "id_formulario")
        ManejoDatos("documentos").guardar(documentos, "id_documento")
        ManejoDatos("practicas").guardar(practicas, "id_practica")

    def _eliminar_registros_estudiante(self, id_estudiante: str) -> None:
        postulaciones = {
            postulacion.id_postulacion: postulacion
            for postulacion in Postulacion.cargar_todos()
            if postulacion.id_estudiante != id_estudiante
        }
        solicitudes = {
            solicitud.id_solicitud: solicitud
            for solicitud in SolicitudAutorizacion.cargar_todos()
            if solicitud.id_estudiante != id_estudiante
        }

        ManejoDatos("postulaciones").guardar(postulaciones, "id_postulacion")
        ManejoDatos("solicitudes").guardar(solicitudes, "id_solicitud")

    def _eliminar_notificaciones_usuario(self, id_usuario: str) -> None:
        notificaciones = {
            notificacion.id_notificacion: notificacion
            for notificacion in Notificacion.cargar_todos()
            if notificacion.id_usuario != id_usuario
        }
        ManejoDatos("notificaciones").guardar(notificaciones, "id_notificacion")

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

