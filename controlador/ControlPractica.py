"""Casos de uso para practicas, actividades y documentos."""

from __future__ import annotations

from datetime import date

from configuracion.ajustes import HORAS_MAXIMAS_PRACTICA, ROLES
from controlador.ControlNotificacion import ControlNotificacion
from modelo.Documentos import Documento, Formulario
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Practica import Actividad, Practica
from modelo.Usuario import Estudiante, Usuario
from utilidades.Excepciones import AutorizacionError, ReglaNegocioError, ValidacionError
from utilidades.IDgenerator import generar_id
from utilidades.ManejoDatos import ManejoDatos


class ControlPractica:
    def crear_practica(
            self,
            id_postulacion: str,
            fecha_inicio: date,
            fecha_fin: date,
            id_tutor_academico: str,
            tutor_empresarial: str,
    ) -> Practica:
        postulacion = Postulacion.obtener_por_id(id_postulacion)
        if postulacion.estado != "aceptada":
            raise ReglaNegocioError("Solo una postulacion aceptada genera una practica.")

        estudiante = Usuario.obtener_por_id(postulacion.id_estudiante)
        if not isinstance(estudiante, Estudiante):
            raise ReglaNegocioError("La practica debe estar asociada a un estudiante.")
        if estudiante.tiene_practica_activa():
            raise ReglaNegocioError("El estudiante ya tiene una practica activa.")
        if not id_tutor_academico or not tutor_empresarial:
            raise ValidacionError("Toda practica requiere tutor academico y tutor empresarial.")
        if fecha_fin < fecha_inicio:
            raise ValidacionError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        oferta = Oferta.obtener_por_id(postulacion.id_oferta)
        empresa = Empresa.obtener_por_id(oferta.id_empresa)
        self._validar_tutor_academico(id_tutor_academico)
        self._validar_tutor_empresarial(tutor_empresarial, empresa.id_empresa)

        practica = Practica(
            id_practica=generar_id("PRA"),
            id_postulacion=id_postulacion,
            id_estudiante=postulacion.id_estudiante,
            id_empresa=oferta.id_empresa,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_tutor_academico=id_tutor_academico,
            tutor_empresarial=tutor_empresarial,
        )
        practica.guardar()

        estudiante.asignar_practica_activa(practica.id_practica)
        estudiante.guardar()
        self._registrar_formulario_inicial(practica, estudiante, empresa)
        carta = self._generar_carta_compromiso_si_requiere(practica, empresa)
        self._notificar_practica_creada(practica, estudiante, empresa)
        if carta is not None:
            self._notificar_carta_compromiso(practica, estudiante, empresa)
        return practica

    def registrar_actividad(self, id_practica: str, descripcion: str, horas: int) -> Actividad:
        practica = Practica.obtener_por_id(id_practica)
        if practica.estado != "activa":
            raise ReglaNegocioError("Solo se registran actividades en practicas activas.")
        if horas <= 0:
            raise ValidacionError("Las horas deben ser mayores a cero.")
        if practica.horas_cumplidas >= HORAS_MAXIMAS_PRACTICA:
            raise ReglaNegocioError("La practica ya completo las 240 horas requeridas.")
        self._validar_horas_actividad(id_practica, horas)

        actividad = Actividad(
            id_actividad=generar_id("ACT"),
            id_practica=id_practica,
            descripcion=descripcion,
            horas=horas,
            fecha=date.today(),
        )
        actividad.guardar()
        return actividad

    def aprobar_actividad(self, id_actividad: str, id_tutor_academico: str) -> Actividad:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if practica.id_tutor_academico != id_tutor_academico:
            raise AutorizacionError("La actividad debe aprobarla el tutor academico asignado.")

        actividad.aprobar(id_tutor_academico)
        actividad.guardar()
        return actividad

    def completar_actividad(self, id_actividad: str, tutor_empresarial: str) -> Actividad:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if practica.tutor_empresarial != tutor_empresarial:
            raise AutorizacionError("La actividad debe completarla el tutor empresarial asignado.")
        if not actividad.aprobada_por_tutor_academico:
            raise ReglaNegocioError(
                "La actividad debe estar aprobada por el tutor academico antes de completarse."
            )
        if actividad.completada_por_tutor_empresarial:
            raise ReglaNegocioError("La actividad ya fue marcada como completada.")
        if practica.horas_cumplidas + actividad.horas > HORAS_MAXIMAS_PRACTICA:
            raise ReglaNegocioError(
                "La actividad supera el maximo de 240 horas permitidas para la practica."
            )

        actividad.completar(tutor_empresarial)
        actividad.guardar()
        practica.horas_cumplidas += actividad.horas
        practica.guardar()
        self._cerrar_practica_si_completo_horas(practica)
        return actividad

    def cambiar_aprobacion_actividad(
            self,
            id_actividad: str,
            aprobada: bool,
            id_tutor_academico: str | None = None,
            es_admin: bool = False,
    ) -> Actividad:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if not es_admin and practica.id_tutor_academico != id_tutor_academico:
            raise AutorizacionError("Solo el tutor academico asignado o el administrador puede cambiar la aprobacion.")
        if not aprobada and actividad.completada_por_tutor_empresarial:
            raise ReglaNegocioError("No se puede quitar la aprobacion de una actividad completada.")

        if aprobada:
            actividad.aprobar(id_tutor_academico or "ADMIN")
        else:
            actividad.aprobada_por_tutor_academico = False
            actividad.id_tutor_academico_aprobador = None
            actividad.fecha_aprobacion = None
        actividad.guardar()
        return actividad

    def cambiar_completado_actividad(
            self,
            id_actividad: str,
            completada: bool,
            tutor_empresarial: str | None = None,
            es_admin: bool = False,
    ) -> Actividad:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if not es_admin and practica.tutor_empresarial != tutor_empresarial:
            raise AutorizacionError("Solo el tutor empresarial asignado o el administrador puede cambiar el completado.")
        if completada:
            return self.completar_actividad(id_actividad, tutor_empresarial or practica.tutor_empresarial)
        if not actividad.completada_por_tutor_empresarial:
            return actividad

        actividad.completada_por_tutor_empresarial = False
        actividad.tutor_empresarial_completador = None
        actividad.fecha_completado = None
        actividad.guardar()
        practica.horas_cumplidas = max(0, practica.horas_cumplidas - actividad.horas)
        if practica.estado == "finalizada" and practica.horas_cumplidas < HORAS_MAXIMAS_PRACTICA:
            practica.estado = "activa"
            estudiante = Usuario.obtener_por_id(practica.id_estudiante)
            if isinstance(estudiante, Estudiante):
                estudiante.asignar_practica_activa(practica.id_practica)
                estudiante.guardar()
        practica.guardar()
        return actividad

    def editar_actividad(
            self,
            id_actividad: str,
            descripcion: str | None = None,
            horas: int | None = None,
            tutor_empresarial: str | None = None,
            es_admin: bool = False,
    ) -> Actividad:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if not es_admin and practica.tutor_empresarial != tutor_empresarial:
            raise AutorizacionError("Solo el tutor empresarial asignado o el administrador puede editar actividades.")
        if actividad.completada_por_tutor_empresarial:
            raise ReglaNegocioError(
                "No se puede editar una actividad aprobada y completada."
            )
        if descripcion is not None:
            actividad.descripcion = descripcion
        if horas is not None:
            if horas <= 0:
                raise ValidacionError("Las horas deben ser mayores a cero.")
            self._validar_horas_actividad(
                practica.id_practica,
                horas,
                id_actividad_excluida=actividad.id_actividad,
            )
            actividad.horas = horas
        actividad.guardar()
        return actividad

    def eliminar_actividad(
            self,
            id_actividad: str,
            tutor_empresarial: str | None = None,
            es_admin: bool = False,
    ) -> None:
        actividad = Actividad.obtener_por_id(id_actividad)
        practica = Practica.obtener_por_id(actividad.id_practica)
        if not es_admin and practica.tutor_empresarial != tutor_empresarial:
            raise AutorizacionError("Solo el tutor empresarial asignado o el administrador puede eliminar actividades.")

        actividades = {
            actividad_existente.id_actividad: actividad_existente
            for actividad_existente in Actividad.cargar_todos()
        }
        actividades.pop(id_actividad, None)
        ManejoDatos("actividades").guardar(actividades, "id_actividad")
        if actividad.completada_por_tutor_empresarial:
            practica.horas_cumplidas = max(0, practica.horas_cumplidas - actividad.horas)
            if practica.estado == "finalizada" and practica.horas_cumplidas < HORAS_MAXIMAS_PRACTICA:
                practica.estado = "activa"
            practica.guardar()

    def validar_actividad(self, id_actividad: str, id_tutor_academico: str) -> Actividad:
        return self.aprobar_actividad(id_actividad, id_tutor_academico)

    def finalizar_practica(self, id_practica: str, observaciones: str = "") -> Practica:
        practica = Practica.obtener_por_id(id_practica)
        self._finalizar_practica(practica)
        self._notificar_practica_completada(practica)
        return practica

    def registrar_formulario(
            self,
            id_practica: str,
            tipo: str,
            observaciones: str = "",
            contenido: str = "",
            calificacion: int | None = None,
    ) -> Formulario:
        Practica.obtener_por_id(id_practica)
        formulario = Formulario(
            id_formulario=generar_id("FOR"),
            id_practica=id_practica,
            tipo=tipo,
            fecha_registro=date.today(),
            observaciones=observaciones,
            contenido=contenido,
            calificacion=calificacion,
        )
        formulario.guardar()
        return formulario

    def emitir_documento(
            self,
            id_practica: str,
            tipo: str,
            gestionado_por: str,
            contenido: str = "",
    ) -> Documento:
        Practica.obtener_por_id(id_practica)
        documento = Documento(
            id_documento=generar_id("DOC"),
            id_practica=id_practica,
            tipo=tipo,
            gestionado_por=gestionado_por,
            fecha_emision=date.today(),
            contenido=contenido,
        )
        documento.guardar()
        return documento

    def _generar_carta_compromiso_si_requiere(
            self,
            practica: Practica,
            empresa: Empresa,
    ) -> Documento | None:
        if empresa.convenio_vigente:
            return None

        estudiante = Usuario.buscar_por_id(practica.id_estudiante)
        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        contenido = "\n".join(
            [
                "Carta compromiso - Practicas preprofesionales",
                f"Practica: {practica.id_practica}",
                f"Estudiante: {estudiante.nombre if estudiante else practica.id_estudiante}",
                f"Empresa: {empresa.nombre_empresa}",
                f"Fecha inicio: {practica.fecha_inicio}",
                f"Fecha fin: {practica.fecha_fin}",
                f"Tutor academico: {tutor_academico.nombre if tutor_academico else practica.id_tutor_academico}",
                f"Tutor empresarial: {tutor_empresarial.nombre if tutor_empresarial else practica.tutor_empresarial}",
                "",
                "La empresa declara su compromiso de facilitar el desarrollo de actividades "
                "formativas del estudiante durante la practica preprofesional, respetando "
                "la planificacion academica y el seguimiento definido por la institucion.",
            ]
        )
        return self.emitir_documento(
            practica.id_practica,
            "Carta compromiso",
            "Coordinador",
            contenido,
        )

    def listar_practicas(self) -> list[Practica]:
        return Practica.cargar_todos()

    def listar_practicas_por_tutor_academico(self, id_tutor_academico: str) -> list[Practica]:
        return ManejoDatos("practicas").filtrar(id_tutor_academico=id_tutor_academico)

    def listar_practicas_por_tutor_empresarial(self, id_tutor_empresarial: str) -> list[Practica]:
        return ManejoDatos("practicas").filtrar(tutor_empresarial=id_tutor_empresarial)

    def calificar_practica(
            self,
            id_practica: str,
            calificacion: int,
            id_tutor_academico: str,
    ) -> Practica:
        practica = Practica.obtener_por_id(id_practica)
        if practica.id_tutor_academico != id_tutor_academico:
            raise AutorizacionError("Solo el tutor academico asignado puede calificar la practica.")
        if practica.estado != "finalizada":
            raise ReglaNegocioError("Solo se puede calificar una practica finalizada.")
        if calificacion < 0 or calificacion > 100:
            raise ValidacionError("La calificacion debe estar entre 0 y 100.")

        practica.calificar(calificacion, id_tutor_academico)
        practica.guardar()
        self._registrar_formularios_finales_si_faltan(practica)
        self._notificar_formularios_finales_enviados(practica)
        return practica

    def listar_formularios_estudiante(self, id_estudiante: str) -> list[Formulario]:
        practicas = ManejoDatos("practicas").filtrar(id_estudiante=id_estudiante)
        ids_practicas = {practica.id_practica for practica in practicas}
        return [
            formulario
            for formulario in Formulario.cargar_todos()
            if formulario.id_practica in ids_practicas
        ]

    def listar_documentos_estudiante(self, id_estudiante: str) -> list[Documento]:
        practicas = ManejoDatos("practicas").filtrar(id_estudiante=id_estudiante)
        ids_practicas = {practica.id_practica for practica in practicas}
        return [
            documento
            for documento in Documento.cargar_todos()
            if documento.id_practica in ids_practicas
        ]

    def obtener_practica_activa_estudiante(self, id_estudiante: str) -> Practica | None:
        estudiante = Usuario.obtener_por_id(id_estudiante)
        if not isinstance(estudiante, Estudiante) or not estudiante.tiene_practica_activa():
            return None

        if estudiante.id_practica_activa:
            practica = Practica.buscar_por_id(estudiante.id_practica_activa)
            if practica is not None and practica.estado == "activa":
                return practica

        practicas = ManejoDatos("practicas").filtrar(
            id_estudiante=id_estudiante,
            estado="activa",
        )
        return practicas[0] if practicas else None

    def obtener_practica_visible_estudiante(self, id_estudiante: str) -> Practica | None:
        practica_activa = self.obtener_practica_activa_estudiante(id_estudiante)
        if practica_activa is not None:
            return practica_activa

        practicas = ManejoDatos("practicas").filtrar(id_estudiante=id_estudiante)
        if not practicas:
            return None

        practicas.sort(key=lambda practica: practica.fecha_inicio, reverse=True)
        return practicas[0]

    def obtener_progreso_estudiante(self, id_estudiante: str) -> dict[str, object]:
        practica = self.obtener_practica_visible_estudiante(id_estudiante)
        if practica is None:
            return {
                "practica": None,
                "horas_requeridas": HORAS_MAXIMAS_PRACTICA,
                "horas_cumplidas": 0,
                "actividades_registradas": 0,
                "actividades_aprobadas": 0,
                "actividades_completadas": 0,
                "actividades_pendientes": 0,
                "actividades": [],
            }

        actividades = self.listar_actividades(practica.id_practica)
        actividades_aprobadas = [
            actividad for actividad in actividades if actividad.aprobada_por_tutor_academico
        ]
        actividades_completadas = [
            actividad for actividad in actividades if actividad.completada_por_tutor_empresarial
        ]
        actividades_pendientes = [
            actividad for actividad in actividades if not actividad.completada_por_tutor_empresarial
        ]

        return {
            "practica": practica,
            "horas_requeridas": HORAS_MAXIMAS_PRACTICA,
            "horas_cumplidas": practica.horas_cumplidas,
            "actividades_registradas": len(actividades),
            "actividades_aprobadas": len(actividades_aprobadas),
            "actividades_completadas": len(actividades_completadas),
            "actividades_pendientes": len(actividades_pendientes),
            "actividades": actividades,
        }

    def listar_progreso_estudiantes(self) -> list[dict[str, object]]:
        resumenes = []
        for practica in self.listar_practicas():
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            empresa = Empresa.buscar_por_id(practica.id_empresa)
            actividades = self.listar_actividades(practica.id_practica)
            resumenes.append(
                {
                    "practica": practica,
                    "estudiante": estudiante,
                    "empresa": empresa,
                    "horas_requeridas": HORAS_MAXIMAS_PRACTICA,
                    "actividades": len(actividades),
                    "actividades_completadas": len(
                        [a for a in actividades if a.completada_por_tutor_empresarial]
                    ),
                }
            )
        return resumenes

    def listar_actividades(self, id_practica: str | None = None) -> list[Actividad]:
        if id_practica is None:
            return Actividad.cargar_todos()
        return ManejoDatos("actividades").filtrar(id_practica=id_practica)

    def obtener_horas_registradas(self, id_practica: str) -> int:
        return sum(actividad.horas for actividad in self.listar_actividades(id_practica))

    def obtener_horas_disponibles_para_registro(self, id_practica: str) -> int:
        return HORAS_MAXIMAS_PRACTICA - self.obtener_horas_registradas(id_practica)

    def _validar_horas_actividad(
            self,
            id_practica: str,
            horas: int,
            id_actividad_excluida: str | None = None,
    ) -> None:
        horas_registradas = 0
        for actividad in self.listar_actividades(id_practica):
            if actividad.id_actividad == id_actividad_excluida:
                continue
            horas_registradas += actividad.horas

        if horas_registradas >= HORAS_MAXIMAS_PRACTICA:
            raise ReglaNegocioError(
                "La practica ya tiene registradas las 240 horas requeridas."
            )
        if horas_registradas + horas > HORAS_MAXIMAS_PRACTICA:
            disponibles = HORAS_MAXIMAS_PRACTICA - horas_registradas
            raise ReglaNegocioError(
                f"La actividad supera las horas disponibles. "
                f"Solo puede registrar hasta {disponibles} horas mas."
            )

    def _cerrar_practica_si_completo_horas(self, practica: Practica) -> None:
        if practica.horas_cumplidas < HORAS_MAXIMAS_PRACTICA:
            return

        self._finalizar_practica(practica)
        self._notificar_practica_completada(practica)

    def _finalizar_practica(self, practica: Practica) -> None:
        ya_finalizada = practica.estado == "finalizada"
        practica.completar()
        practica.guardar()

        estudiante = Usuario.obtener_por_id(practica.id_estudiante)
        if isinstance(estudiante, Estudiante):
            estudiante.liberar_practica_activa()
            if not ya_finalizada:
                estudiante.practicas_previas += 1
            estudiante.guardar()

    def _notificar_practica_completada(self, practica: Practica) -> None:
        notificaciones = ControlNotificacion()
        estudiante = Usuario.obtener_por_id(practica.id_estudiante)
        mensaje = (
            f"La practica {practica.id_practica} completo "
            f"{HORAS_MAXIMAS_PRACTICA} horas y fue finalizada. El tutor academico "
            "debe registrar la calificacion para emitir los formularios finales."
        )
        notificaciones.crear_notificacion(estudiante.id_usuario, "Practica completada", mensaje, "practica")

        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        if tutor_academico is not None:
            notificaciones.crear_notificacion(
                tutor_academico.id_usuario,
                "Practica completada",
                mensaje,
                "practica",
            )

        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        notificaciones.crear_notificacion(
            practica.tutor_empresarial,
            "Practica completada",
            mensaje,
            "practica",
            validar_usuario=tutor_empresarial is not None,
        )

        for usuario in Usuario.cargar_todos():
            if usuario.rol == ROLES["COORDINADOR"]:
                notificaciones.crear_notificacion(
                    usuario.id_usuario,
                    "Practica completada",
                    mensaje,
                    "practica",
                )

    def _notificar_practica_creada(
            self,
            practica: Practica,
            estudiante: Estudiante,
            empresa: Empresa,
    ) -> None:
        notificaciones = ControlNotificacion()
        mensaje = (
            f"Se creo la practica {practica.id_practica} para {empresa.nombre_empresa}. "
            f"Periodo: {practica.fecha_inicio} a {practica.fecha_fin}."
        )
        notificaciones.crear_notificacion(
            estudiante.id_usuario,
            "Practica activa asignada",
            mensaje,
            "practica",
        )

        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        if tutor_academico is not None:
            notificaciones.crear_notificacion(
                tutor_academico.id_usuario,
                "Nueva practica asignada",
                f"{mensaje} Estudiante: {estudiante.nombre}.",
                "practica",
            )

        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        if tutor_empresarial is not None:
            notificaciones.crear_notificacion(
                tutor_empresarial.id_usuario,
                "Nueva practica asignada",
                f"{mensaje} Estudiante: {estudiante.nombre}.",
                "practica",
            )

        for usuario in Usuario.cargar_todos():
            if usuario.rol == ROLES["COORDINADOR"]:
                notificaciones.crear_notificacion(
                    usuario.id_usuario,
                    "Practica creada",
                    f"{mensaje} Estudiante: {estudiante.nombre}.",
                    "practica",
                )

    def _registrar_formulario_inicial(
            self,
            practica: Practica,
            estudiante: Estudiante,
            empresa: Empresa,
    ) -> Formulario:
        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        contenido = "\n".join(
            [
                "Formulario 1 - Inicio de practica",
                f"Estudiante: {estudiante.nombre}",
                f"Fecha inicio: {practica.fecha_inicio}",
                f"Fecha fin: {practica.fecha_fin}",
                f"Empresa: {empresa.id_empresa} - {empresa.nombre_empresa}",
                f"Tutor academico: {tutor_academico.nombre if tutor_academico else practica.id_tutor_academico}",
                f"Tutor empresarial: {tutor_empresarial.nombre if tutor_empresarial else practica.tutor_empresarial}",
            ]
        )
        formulario = self.registrar_formulario(
            practica.id_practica,
            "Formulario 1",
            "Registro inicial enviado al estudiante",
            contenido,
        )
        ControlNotificacion().crear_notificacion(
            estudiante.id_usuario,
            "Formulario 1 enviado",
            "Se envio a su correo el Formulario 1 con los datos de inicio de la practica.",
            "formulario",
        )
        return formulario

    def _registrar_formularios_finales_si_faltan(self, practica: Practica) -> None:
        formularios = ManejoDatos("formularios").filtrar(id_practica=practica.id_practica)
        tipos_existentes = {formulario.tipo for formulario in formularios}
        estudiante = Usuario.obtener_por_id(practica.id_estudiante)
        empresa = Empresa.obtener_por_id(practica.id_empresa)
        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        coordinador = self._obtener_nombre_coordinador()
        actividades = self.listar_actividades(practica.id_practica)
        actividades_texto = "\n".join(
            [
                f"- {actividad.fecha}: {actividad.descripcion} ({actividad.horas} horas)"
                for actividad in actividades
                if actividad.completada_por_tutor_empresarial
            ]
        ) or "No hay actividades completadas registradas."

        if "Formulario 2" not in tipos_existentes:
            contenido_2 = "\n".join(
                [
                    "Formulario 2 - Evaluacion de practica",
                    f"Estudiante: {estudiante.nombre if isinstance(estudiante, Estudiante) else practica.id_estudiante}",
                    f"Practica: {practica.id_practica}",
                    f"Empresa: {empresa.nombre_empresa}",
                    f"Tutor academico: {tutor_academico.nombre if tutor_academico else practica.id_tutor_academico}",
                    f"Calificacion: {practica.calificacion}/100",
                    "Actividades desarrolladas:",
                    actividades_texto,
                ]
            )
            self.registrar_formulario(
                practica.id_practica,
                "Formulario 2",
                "Evaluacion final del tutor academico",
                contenido_2,
                practica.calificacion,
            )

        if "Formulario 3" not in tipos_existentes:
            contenido_3 = "\n".join(
                [
                    "Formulario 3 - Culminacion de practica",
                    f"Practica: {practica.id_practica}",
                    f"Fecha fin: {practica.fecha_fin}",
                    f"Empresa: {empresa.nombre_empresa}",
                    f"Coordinador: {coordinador}",
                    f"Tutor academico: {tutor_academico.nombre if tutor_academico else practica.id_tutor_academico}",
                    f"Tutor empresarial: {tutor_empresarial.nombre if tutor_empresarial else practica.tutor_empresarial}",
                    f"Calificacion final: {practica.calificacion}/100",
                ]
            )
            self.registrar_formulario(
                practica.id_practica,
                "Formulario 3",
                "Culminacion formal de la practica",
                contenido_3,
                practica.calificacion,
            )

        practica.formularios_finales_enviados = True
        practica.guardar()

    def _notificar_formularios_finales_enviados(self, practica: Practica) -> None:
        estudiante = Usuario.obtener_por_id(practica.id_estudiante)
        ControlNotificacion().crear_notificacion(
            estudiante.id_usuario,
            "Formularios finales enviados",
            (
                "Se enviaron a su correo los Formularios 2 y 3 de culminacion "
                f"con calificacion {practica.calificacion}/100."
            ),
            "formulario",
        )

    def _notificar_carta_compromiso(
            self,
            practica: Practica,
            estudiante: Estudiante,
            empresa: Empresa,
    ) -> None:
        ControlNotificacion().crear_notificacion(
            estudiante.id_usuario,
            "Carta compromiso enviada",
            (
                f"La empresa {empresa.nombre_empresa} no tiene convenio vigente. "
                "Se genero y envio a su correo la carta compromiso asociada a la practica."
            ),
            "documento",
        )

    def _obtener_nombre_coordinador(self) -> str:
        for usuario in Usuario.cargar_todos():
            if usuario.rol == ROLES["COORDINADOR"]:
                return usuario.nombre
        return "Coordinador no registrado"

    def _validar_tutor_academico(self, id_tutor_academico: str) -> None:
        tutor = Usuario.obtener_por_id(id_tutor_academico)
        if tutor.rol != ROLES["TUTOR_ACADEMICO"]:
            raise ReglaNegocioError("El tutor academico asignado debe tener rol de tutor academico.")
        if not getattr(tutor, "activo", True):
            raise ReglaNegocioError("El tutor academico asignado debe estar activo.")

    def _validar_tutor_empresarial(self, id_tutor_empresarial: str, id_empresa: str) -> None:
        tutor = Usuario.obtener_por_id(id_tutor_empresarial)
        if tutor.rol != ROLES["TUTOR_EMPRESARIAL"]:
            raise ReglaNegocioError("El tutor empresarial asignado debe tener rol de tutor empresarial.")
        if not getattr(tutor, "activo", True):
            raise ReglaNegocioError("El tutor empresarial asignado debe estar activo.")
        if getattr(tutor, "id_empresa", "") != id_empresa:
            raise ReglaNegocioError("El tutor empresarial debe pertenecer a la misma empresa de la oferta.")
